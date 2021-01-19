from typing import Optional
from fastapi import FastAPI, Request, Response,  status, HTTPException
import datetime
from main import app
from .service import blockchain_service
from .models import Block


# @app.post('/api/genesis-block', status_code=status.HTTP_201_CREATED)
# def handle_request():

#   response = { "msg": "OK" }
#   block = Block(proof=20, previous_hash="0000")

#   block.save()
#   return response


@app.get('/api/validate-blockchain', status_code=status.HTTP_200_OK)
def handle_request():

    response = {}

    chain = list(Block.select().dicts())
    is_valid = blockchain_service.is_chain_valid(chain=chain)
    
    response['valid'] = is_valid
    return response
    
@app.get('/api/blockchain', status_code=status.HTTP_200_OK)
def handle_request():

    blocks = list(Block.select().dicts())
    return { "blocks": blocks }


@app.get("/api/mine-block", status_code=status.HTTP_201_CREATED)
def handle_request():

    previouse_block = Block.select().order_by(Block.index.desc()).dicts().get()
    previouse_block['date'] = str(previouse_block['date'])
    previous_proof= previouse_block["proof"]

    proof = blockchain_service.proof_of_work(previous_proof=previous_proof)
    previous_hash = blockchain_service.hash_block(block=previouse_block)

    mined_block = blockchain_service.create_block(previous_hash=previous_hash, proof=proof)
    return mined_block

