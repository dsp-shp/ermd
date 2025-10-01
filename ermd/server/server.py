from contextlib import asynccontextmanager
from pathlib import Path

import logging

from fastapi import FastAPI, Body, Request
from fastapi.params import File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from ermd.server.utils import parse_markdown


logger = logging.getLogger(__name__)

def create_app() -> FastAPI:
    static = Path(__file__).parent.parent / "client/build/static"

    app = FastAPI()

    app.mount("/static", StaticFiles(directory=static, html=True, check_dir=False), name="static")

    @app.get("/")
    async def root():
        return HTMLResponse((static.parent / "index.html").read_text())

    @app.post("/api/parse")
    async def parse(text: str = Body(..., embed=True)):
        return parse_markdown(text)

    return app


app = create_app()
