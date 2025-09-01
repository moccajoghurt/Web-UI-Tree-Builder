from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from tree_host.actions import tree

app = FastAPI()


class RequestData(BaseModel):
    jsonl: dict


@app.get("/")
async def index():
    html_content = await tree.load_index()
    return HTMLResponse(content=html_content, media_type="text/html")


@app.post("/update-tree")
async def update(data: RequestData):
    html_content = await tree.update_tree(data.jsonl)
    return HTMLResponse(content=html_content, media_type="text/html")
