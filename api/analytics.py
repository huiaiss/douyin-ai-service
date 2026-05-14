import json
from datetime import date
from fastapi import APIRouter
from pydantic import BaseModel
from db.models import Analytics

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


class RecordRequest(BaseModel):
    conversations: int = 1
    response_time: float = 0.0
    sentiment: str = "中性"
    question: str = ""


@router.post("/record")
def record_analytics(body: RecordRequest):
    today = date.today()
    entry = Analytics.get_or_none(Analytics.date == today)

    if entry:
        prev_count = entry.convo_count
        new_count = prev_count + 1
        entry.avg_response = (
            (entry.avg_response * prev_count) + body.response_time
        ) / new_count if new_count > 0 else body.response_time

        prev_pos = entry.pos_ratio * prev_count
        new_pos = prev_pos + (1 if body.sentiment == "正面" else 0)
        entry.pos_ratio = new_pos / new_count

        questions = json.loads(entry.top_questions or "[]")
        if body.question and body.question not in questions:
            questions.append(body.question)
            if len(questions) > 10:
                questions = questions[-10:]
        entry.top_questions = json.dumps(questions, ensure_ascii=False)
        entry.convo_count = new_count
        entry.save()
    else:
        pos = 1.0 if body.sentiment == "正面" else 0.0
        entry = Analytics.create(
            date=today,
            convo_count=1,
            avg_response=body.response_time,
            pos_ratio=pos,
            top_questions=json.dumps(
                [body.question] if body.question else [],
                ensure_ascii=False
            ),
        )

    return {
        "date": str(entry.date),
        "convo_count": entry.convo_count,
        "avg_response": round(entry.avg_response, 2),
        "pos_ratio": round(entry.pos_ratio, 2),
        "top_questions": json.loads(entry.top_questions or "[]"),
    }


@router.get("")
def get_analytics():
    today = date.today()
    entry = Analytics.get_or_none(Analytics.date == today)
    if not entry:
        return {
            "date": str(today), "convo_count": 0,
            "avg_response": 0.0, "pos_ratio": 0.0,
            "top_questions": [],
        }
    return {
        "date": str(entry.date),
        "convo_count": entry.convo_count,
        "avg_response": round(entry.avg_response, 2),
        "pos_ratio": round(entry.pos_ratio, 2),
        "top_questions": json.loads(entry.top_questions or "[]"),
    }
