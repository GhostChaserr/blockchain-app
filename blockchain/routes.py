import json
import datetime
from typing import Optional
from fastapi import FastAPI, Request, Response,  status, HTTPException
from main import app
from .service import blockchain_service
from .models import Block, Transaction
from peewee import JOIN, prefetch
from playhouse.shortcuts import model_to_dict, dict_to_model
from uuid import uuid4

from .types import  (
  TransactionDto, 
  TransactionResponse, 
  ConnectNodesDto, 
  ConnectNodeRessponse,
  ReplaceChainResponse
)



# ამ მანქანის მისამართი რომელიც 5200 სზე ეშვება.
# მაინერი როცა ბლოკს ამაინინგებს, მაინერი ბიტტკოინს იღღებს
# შესაბამისადდ, ტრანზაქცია იქმნება, ამ ნოუდსა და მაინერს შორის.
node_adress = str(uuid4()).replace('-', '')

@app.get('/api/validate-blockchain', status_code=status.HTTP_200_OK)
def handle_request():

    response = {}

    chain = list(Block.select().dicts())
    is_valid = blockchain_service.is_chain_valid(chain=chain)
    
    response['valid'] = is_valid
    return response
    
@app.get('/api/blockchain', status_code=status.HTTP_200_OK)
def handle_request():

    # DB later.
    # blocks = list(Block.select(Block).dicts())
    # for block in blocks:
    #   transactions = list(Transaction.select().where(Transaction.block_id == block.get('index')).dicts())
    #   block['transactions'] = transactions
      
    length = len(blockchain_service.chain)
    return { "blocks": blockchain_service.chain, "length": length }


@app.get("/api/mine-block", status_code=status.HTTP_201_CREATED)
def handle_request():

    # DB later.
    # previouse_block = Block.select().order_by(Block.index.desc()).dicts().get()
    # previouse_block['date'] = str(previouse_block['date'])
    # previous_proof= previouse_block["proof"]

    previous_block = blockchain_service.get_previous_block()
    previous_proof = previous_block['proof']

    proof = blockchain_service.proof_of_work(previous_proof=previous_proof)
    previous_hash = blockchain_service.hash_block(block=previous_block)

    blockchain_service.add_transaction(sender=node_adress, receiver=node_adress, amount=15)
    mined_block = blockchain_service.create_block(previous_hash=previous_hash, proof=proof)
    # DB later.
    # transaction = blockchain_service.add_transaction(
    #   sender='george',
    #   receiver='george',
    #   block_id=29,
    #   amount=200
    # )
    
    return mined_block


# 1. ქმნის ახალ ტრანზაქციას, sender, receiver, aamount ის მიწოდებით.
@app.post('/api/transactions', status_code=status.HTTP_201_CREATED, response_model=TransactionResponse)
def handle_request(transactionDto: TransactionDto):

  # ინდექსი ბლოკის რომელსაც ეკუთვნისს ეს ტრანზაქცია
  index = blockchain_service.add_transaction(
    sender=transactionDto.sender,
    receiver=transactionDto.receiver,
    amount=transactionDto.amount
  )

  return { 
      "block": index, 
      "message": f'transaction was added for block index {index}' 
    }

@app.post('/api/connect-node', status_code=status.HTTP_201_CREATED, response_model=ConnectNodeRessponse)
def handle_request(nodesDto: ConnectNodesDto):

  for node in nodesDto.nodes:
    blockchain_service.add_node(address=node)

  return {
    'message': 'Node added',
    'nodes': blockchain_service.nodes
  }


@app.post('/api/replace-chain', status_code=status.HTTP_200_OK, response_model=ReplaceChainResponse)
def handle_request():

  is_replaced = blockchain_service.replace_chain()
  if is_replaced:
    return { 'message': 'chain replaced', 'new_chain': blockchain_service.chain }

  return { 'message': 'not replaced', 'old_chain': blockchain_service.chain }