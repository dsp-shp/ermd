from contextlib import asynccontextmanager
from pathlib import Path

import logging

from fastapi import FastAPI, Body, Request
from fastapi.params import File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse

from ermd.server.utils import parse_markdown, Entity, Relation, order_relations


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.entities = {}
    app.state.relations = []

    yield

app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         # "*",
#         "http://localhost:3000"
#     ],  # фронт адрес
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

static = Path(__file__).parent.parent / "client/build/static"

app.mount("/static", StaticFiles(directory=static, html=True, check_dir=False), name="static")

@app.get("/")
async def root():
    return HTMLResponse((static.parent / "index.html").read_text())

@app.post("/api/parse")
async def parse(text: str = Body(..., embed=True)):
    app.state.entities, app.state.relations = parse_markdown(text)
    return order_relations(app.state.relations)
