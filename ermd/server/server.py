from contextlib import asynccontextmanager

import logging

from fastapi import FastAPI, Body, Request
from fastapi.middleware.cors import CORSMiddleware

from ermd.server.utils import parse_markdown, Entity, Relation, order_relations


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.entities = {}
    app.state.relations = []

    yield


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        # "*",
        "http://localhost:3000"
    ],  # фронт адрес
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/parse")
async def parse(text: str = Body(..., embed=True)):
    app.state.entities, app.state.relations = parse_markdown(text)
    return order_relations(app.state.relations)
    # {
    #     "entities": [x.to_dict() for x in app.state.entities.values()],
    #     "relations": [x.to_dict() for x in order_relations(app.state.relations)]
    # }
