from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import logging
from .library.helpers import *
from app.routers import errors

from app.core.logging import init_loggers
import os

init_loggers()
log = logging.getLogger("error-analysis")

app = FastAPI()

here = os.path.dirname(os.path.abspath(__file__))
root = os.path.dirname(here)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data")

app.include_router(errors.router)


@app.middleware("http")
async def load_app_data(request: Request, call_next):
    """
    Middleware to ensure that data is always loaded
    """
    # If we don't have data loaded, load it
    if not hasattr(request.app, "error_clusters"):
        log.info("Loading cluster errors lookup")
        request.app.error_clusters = load_errors_lookup(root)
    if not hasattr(request.app, "spec_errors"):
        request.app.spec_errors = load_errors_specs_lookup(root)
    return await call_next(request)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    data = openfile("index.md")
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "data": data,
            "error_clusters": request.app.error_clusters,
        },
    )


@app.get("/page/{page_name}", response_class=HTMLResponse)
async def show_page(request: Request, page_name: str):
    data = openfile(page_name + ".md")
    return templates.TemplateResponse("page.html", {"request": request, "data": data})
