from fastapi import FastAPI, Request, Form, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import yaml
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates/")


def load_spec(root, digest):
    """
    Given a spec id, load from the data directory
    """
    spec_file = os.path.join(root, "data", "spec_files", "errors", "%s.yaml" % digest)
    if os.path.exists(spec_file):
        with open(spec_file, "r") as fd:
            content = yaml.safe_load(fd.read())
        return content


def load_features(root, digest):
    """
    Given a spec id, load features for it
    """
    spec_file = os.path.join(
        root, "data", "feature-ranking", "tfidf", "cluster-feats-%s.json" % digest
    )
    if os.path.exists(spec_file):
        with open(spec_file, "r") as fd:
            content = json.loads(fd.read())
        return content


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
