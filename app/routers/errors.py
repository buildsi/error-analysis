from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import json

from .helpers import (
    load_spec,
    load_features,
    find_single_nearest_good_spec,
    find_cluster_nearest_good_spec,
    load_spec_features,
)


router = APIRouter()
templates = Jinja2Templates(directory="templates/")


@router.get(
    "/analysis/working/single/similar/{error_spec_hash}/cluster/{cluster_id}",
    response_class=HTMLResponse,
)
def find_similar_working_specs(request: Request, error_spec_hash: str, cluster_id: int):
    """
    Given an error single spec id, find the most similar _working_ spec
    """
    error_spec_features = load_spec_features(
        request.app.root, error_spec_hash, spectype="errors"
    )
    error_spec_features = dict.fromkeys(error_spec_features, 1)
    good_spec_features, good_spec_uid, score = find_single_nearest_good_spec(
        request.app.root, error_spec_features, cluster_id, request.app.good_specs
    )
    return spec_comparison_view(
        request,
        good_spec_features,
        error_spec_features,
        good_spec_uid,
        score,
        cluster_id,
        comptype="single",
    )


@router.get("/analysis/working/similar/{cluster_id}", response_class=HTMLResponse)
def find_similar_cluster_specs(request: Request, cluster_id: int):
    """
    Given an errors cluster id, find similar _working_ specs
    """
    # Load the feature weights here so we can compare them
    error_spec_features = load_features(request.app.root, cluster_id)
    good_spec_features, good_spec_uid, score = find_cluster_nearest_good_spec(
        error_spec_features, request.app.good_specs
    )
    return spec_comparison_view(
        request,
        good_spec_features,
        error_spec_features,
        good_spec_uid,
        score,
        cluster_id,
        comptype="cluster",
    )


def spec_comparison_view(
    request: Request,
    good_spec_features,
    error_spec_features,
    good_spec_uid,
    score,
    cluster_id,
    comptype,
):
    """
    Shared view to return a good spec and comparison metrics
    """
    # Load the good spec to show the user
    good_spec = load_spec(request.app.root, good_spec_uid, spectype="working")

    # Assemble a set of features we can compare
    # For errors that are != 0 and overlap, we can create a plot
    overlap = {}

    # In the error spec but not the good spec
    # Features will overlap, but having a value == 0 is akin to not present
    error_not_good = {}
    for feat, value in error_spec_features.items():
        if feat in good_spec_features:
            good_value = good_spec_features[feat]
            if value != 0 or good_value != 0:
                overlap[feat] = {"error": value, "good_value": good_value}
        elif feat not in good_spec_features and value != 0:
            error_not_good[feat] = value

    # Sort by feature importance for error spec
    overlap = sorted(overlap.items(), key=lambda x: x[1]["error"])

    # in the good spec but not the error
    good_not_error = {}
    for feat, value in good_spec_features.items():
        if feat not in error_spec_features and value != 0:
            good_not_error[feat] = value

    # Only return non-zero features and sort by value
    return templates.TemplateResponse(
        "analysis/diff.html",
        context={
            "request": request,
            "cluster_id": cluster_id,
            "overlap": overlap,
            "good_spec": json.dumps(good_spec),
            "good_spec_uid": good_spec_uid,
            "good_not_error": good_not_error,
            "comptype": comptype,
        },
    )


@router.get("/analysis/features/{cluster_id}", response_class=HTMLResponse)
def view_features(request: Request, cluster_id: int):
    """
    Clicking to see features for a cluster will show the ranked list.
    """
    features = load_features(request.app.root, cluster_id)

    # Only return non-zero features and sort by value
    if features:
        features = {k: v for k, v in features.items() if v != 0.0}
        features = sorted(features.items(), key=lambda x: x[1], reverse=True)
    return templates.TemplateResponse(
        "analysis/features.html",
        context={"request": request, "cluster_id": cluster_id, "features": features},
    )


@router.get("/analysis/errors/{cluster_id}", response_class=HTMLResponse)
def view_error(request: Request, cluster_id: int):
    """
    Clicking an error (assigned to a cluster) should show all the specs assigned.
    """
    # Find spec ids that match the cluster
    specs = {}
    for spec_hash, cid in request.app.spec_errors.items():
        if cid == cluster_id:
            spec = load_spec(request.app.root, spec_hash)
            if spec:
                # Ensure we pretty print it
                specs[spec_hash] = json.dumps(spec, indent=4)
    return templates.TemplateResponse(
        "analysis/error-cluster.html",
        context={"request": request, "cluster_id": cluster_id, "specs": specs},
    )
