from db.models import db, Customer, Conversation, Message, Knowledge, Product, Order, Analytics


def init_db():
    db.connect()
    db.create_tables([
        Customer, Conversation, Message,
        Knowledge, Product, Order, Analytics
    ])
    db.close()


if __name__ == "__main__":
    init_db()
    print("Database tables created.")
