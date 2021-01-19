from fastapi import FastAPI
from db.conn import db

# App
app = FastAPI()

from blockchain.models import Block

@app.on_event("startup")
async def handle_request():

    # Connect to db.
    db.connect()

    # Register table.
    db.create_tables([Block])

@app.on_event("shutdown")
async def handle_request():
    db.close()

import blockchain.routes
