from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from tree_host.actions import tree


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ActionItem(BaseModel):
    id: str
    parent: str | None
    path: list[str]
    title: str
    route: str
    type: str


@app.get("/")
async def index():
    html_content = await tree.load_index()
    return HTMLResponse(content=html_content, media_type="text/html")


@app.post("/update-tree")
async def update(data: ActionItem):
    html_content = await tree.update_tree(data.model_dump())
    return HTMLResponse(content=html_content, media_type="text/html")
