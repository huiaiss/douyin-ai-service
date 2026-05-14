import os
from config import Config
from db.models import (
    db, Customer, Conversation, Message,
    Knowledge, Product, Order, Analytics
)

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_convo_customer ON conversation (customer_id);",
    "CREATE INDEX IF NOT EXISTS idx_message_convo ON message (convo_id);",
    "CREATE INDEX IF NOT EXISTS idx_order_customer ON \"order\" (customer_id);",
    "CREATE INDEX IF NOT EXISTS idx_knowledge_category ON knowledge (category);",
    "CREATE INDEX IF NOT EXISTS idx_product_category ON product (category);",
]


def init_db():
    os.makedirs(Config.DATA_DIR, exist_ok=True)
    db.init(Config.DATABASE_PATH)
    db.connect()
    try:
        db.create_tables([
            Customer, Conversation, Message,
            Knowledge, Product, Order, Analytics
        ])
        for idx_sql in INDEXES:
            db.execute_sql(idx_sql)
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("Database tables and indexes created.")
