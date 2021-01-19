
import datetime
from db.conn import db
from peewee import ( 
  Model, 
  PrimaryKeyField, 
  TextField, 
  CharField, 
  ForeignKeyField, 
  DateField, 
  IntegerField,
  TimestampField,
  DateTimeField
)

class Block(Model):
  index = PrimaryKeyField()
  proof = IntegerField()
  date = DateTimeField(default=datetime.datetime.now().strftime('%Y-%m-%d'))
  previous_hash = CharField(max_length=255)

  class Meta:
    database = db 