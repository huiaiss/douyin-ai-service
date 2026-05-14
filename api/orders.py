from fastapi import APIRouter, HTTPException
from db.models import Order

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("")
def list_orders(status: str | None = None, limit: int = 20):
    q = Order.select()
    if status:
        q = q.where(Order.status == status)
    return [{
        "id": o.id, "order_no": o.order_no, "status": o.status,
        "amount": o.amount, "created_at": str(o.created_at),
        "customer_id": o.customer_id,
    } for o in q.order_by(Order.created_at.desc()).limit(limit)]


@router.get("/{order_id}")
def get_order(order_id: int):
    o = Order.get_or_none(Order.id == order_id)
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    return {
        "id": o.id, "order_no": o.order_no, "status": o.status,
        "amount": o.amount, "customer_id": o.customer_id,
        "created_at": str(o.created_at),
    }


@router.get("/track/{order_no}")
def track_order(order_no: str):
    o = Order.get_or_none(Order.order_no == order_no)
    if not o:
        raise HTTPException(status_code=404, detail="Order not found")
    import json
    return {
        "order_no": o.order_no,
        "status": o.status,
        "amount": o.amount,
        "logistics": json.loads(o.logistics or "{}"),
        "created_at": str(o.created_at),
    }
