from fastapi import FastAPI, Request, Form, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates/")


@router.get("/analysis/errors/{cluster_id}", response_class=HTMLResponse)
def view_error(request: Request, cluster_id: int):
    """
    Clicking an error (assigned to a cluster) should show all the specs assigned.
    """
    # Find spec ids that match the cluster
    specs = []
    for spec_hash, cid in request.app.spec_errors.items():
        if cid == cluster_id:
            specs.append(spec_hash)
    return templates.TemplateResponse(
        "error-cluster.html",
        context={"request": request, "cluster_id": cluster_id, "specs": specs},
    )
