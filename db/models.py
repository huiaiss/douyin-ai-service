import datetime
from peewee import (
    SqliteDatabase, Model, CharField, TextField,
    IntegerField, FloatField, DateTimeField, DateField,
    ForeignKeyField, BlobField, SQL
)
from config import Config

db = SqliteDatabase(None)


def _utcnow():
    return datetime.datetime.now(datetime.timezone.utc)


class BaseModel(Model):
    class Meta:
        database = db


class Customer(BaseModel):
    platform_uid = CharField(max_length=128, unique=True)
    nickname = CharField(max_length=128, default="")
    tags = TextField(default="[]")
    order_count = IntegerField(default=0)


class Conversation(BaseModel):
    customer = ForeignKeyField(Customer, backref="conversations")
    platform = CharField(max_length=32, default="douyin")
    status = CharField(max_length=16, default="active")
    created_at = DateTimeField(default=_utcnow)
    updated_at = DateTimeField(default=_utcnow)


class Message(BaseModel):
    convo = ForeignKeyField(Conversation, backref="messages")
    role = CharField(max_length=16)
    content = TextField()
    sentiment = CharField(max_length=16, null=True)
    source = CharField(max_length=32, null=True)
    created_at = DateTimeField(default=_utcnow)


class Knowledge(BaseModel):
    category = CharField(max_length=64)
    title = CharField(max_length=256)
    content = TextField()
    embedding = BlobField(null=True)
    created_at = DateTimeField(default=_utcnow)


class Product(BaseModel):
    name = CharField(max_length=256)
    description = TextField(default="")
    price = FloatField(default=0.0)
    image_url = TextField(default="")
    category = CharField(max_length=64, default="")
    tags = TextField(default="[]")
    embedding = BlobField(null=True)
    created_at = DateTimeField(default=_utcnow)


class Order(BaseModel):
    customer = ForeignKeyField(Customer, backref="orders")
    order_no = CharField(max_length=64, unique=True)
    status = CharField(max_length=32)
    amount = FloatField(default=0.0)
    logistics = TextField(default="{}")
    created_at = DateTimeField(default=_utcnow)


class Analytics(BaseModel):
    date = DateField(unique=True)
    convo_count = IntegerField(default=0)
    avg_response = FloatField(default=0.0)
    pos_ratio = FloatField(default=0.0)
    top_questions = TextField(default="[]")
