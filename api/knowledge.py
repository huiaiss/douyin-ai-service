from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.models import Knowledge
from config import Config

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


class KnowledgeCreate(BaseModel):
    category: str
    title: str
    content: str


class KnowledgeUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    category: str | None = None


@router.post("", status_code=201)
def create_knowledge(body: KnowledgeCreate):
    k = Knowledge.create(
        category=body.category,
        title=body.title,
        content=body.content,
    )
    return {"id": k.id, "category": k.category, "title": k.title,
            "content": k.content, "created_at": str(k.created_at)}


@router.get("")
def list_knowledge(category: str | None = None):
    q = Knowledge.select()
    if category:
        q = q.where(Knowledge.category == category)
    return [{"id": k.id, "category": k.category, "title": k.title,
             "content": k.content, "created_at": str(k.created_at)}
            for k in q.order_by(Knowledge.created_at.desc())]


@router.get("/{knowledge_id}")
def get_knowledge(knowledge_id: int):
    k = Knowledge.get_or_none(Knowledge.id == knowledge_id)
    if not k:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    return {"id": k.id, "category": k.category, "title": k.title,
            "content": k.content, "created_at": str(k.created_at)}


@router.put("/{knowledge_id}")
def update_knowledge(knowledge_id: int, body: KnowledgeUpdate):
    k = Knowledge.get_or_none(Knowledge.id == knowledge_id)
    if not k:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    if body.title is not None:
        k.title = body.title
    if body.content is not None:
        k.content = body.content
    if body.category is not None:
        k.category = body.category
    k.save()
    return {"id": k.id, "category": k.category, "title": k.title,
            "content": k.content, "created_at": str(k.created_at)}


@router.delete("/{knowledge_id}")
def delete_knowledge(knowledge_id: int):
    k = Knowledge.get_or_none(Knowledge.id == knowledge_id)
    if not k:
        raise HTTPException(status_code=404, detail="Knowledge not found")
    k.delete_instance()
    return {"deleted": True}
