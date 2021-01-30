import json
import datetime
import hashlib
import requests
from typing import List

from uuid import uuid4
from urllib.parse import urlparse
from db.conn import db
from .models import Block, Transaction

from .types import IBlock, ITransaction

class BlockchainService:
  def __init__(self):
    self.chain: List[IBlock] = []
    self.transactions: List[ITransaction] = []
    self.nodes = set()

    self.create_block(previous_hash="0000",proof=120)
  
  def replace_chain(self):

    # მანქანების ნეთვორქი.
    network = self.nodes

    # შევინახავთ ყველაზე გრძელ ჯაჭვს.
    longest_chain: List[IBlock] = None

    # რაც მანქანაზეა, მაგ ჯაჭვის სიგრძე გვჭირდება შესადარებლად.
    max_length: int = len(self.nodes)

    # გადავუაროთ ნოუდებს სათითაოთ
    for node in network:

      # ვნახოთ სათითოად მანქანებზე რა სიგრძის ჯაჭვს ინახავენ.
      # ენდფოინთი აბრუნებს სიგრზესა და მთლიან ჯაჭვს.
      response = requests.get(f'http://{node}/api/blockchain')
      if response.status_code == 200:

        # რესფონსიდან ამოვიღოთ ჯაჭვის სიგრძე.
        length: int = response.json()['length']

        # რესფონსიდან ამოვიღოთ მთლიანი ჯაჭვი.
        chain: List[IBlock] = response.json()['chain']

        # ჯერ ვამოწმებთ მანქანაზე მყოფი ჯაჭვის სიგრძე თუ უფრო მეტია არსებულზე და ამასთან ჯაჭვი ნამვდილად ვალიდურია.
        if length > max_length and self.is_chain_valid(chain):

          # თუ ასეა, ახალი ჯაჭვი ხდება კონკრეტული მანქანის და ასევე ხდება სიგრძის განახლება.
          max_length = length
          longest_chain = chain

    # ვახდენთ ჯაჭვის განახლებას, სხვა მანქანის ჯაჭვით სადაც ყველაზე დიდი აღმოჩნდა.
    if longest_chain:
      self.chain = longest_chain
      return True

    return False

  # მისამართი შეიცავს სრულ url ს. http://127.0.0:50000
  def add_node(self, address: str):

    # netloc - მანქანის ip + port
    parsed_url = urlparse(address)
    self.nodes.add(parsed_url.netloc)

  # ტრანზაქცია მოიცავს გამგზავნს, მიმღებს, რაოდენობას
  def add_transaction(self, sender: str, receiver: str, amount: int):

    # transaction = Transaction(
    #   sender=sender,
    #   receiver=receiver,
    #   amount=amount,
    #   block_id=block_id 
    # )

    transaction: ITransaction = {
      'sender': sender,
      'receiver': receiver,
      'amount': amount,
      'timestamp': str(datetime.datetime.now())
    }

    self.transactions.append(transaction)
    previouse_block: IBlock = self.get_previous_block()
    return previouse_block['index'] + 1

    # transaction.save()
    # print(transaction.block_id)

    # self.transactions.append(transaction.id)

    # დავქვერავთ ბოლო ინდექსს.
    # previouse_block = Block.select().order_by(Block.index.desc()).dicts().get()

    # ახალი დამაინინგებული ბლოკის ინდექსი. არსებულს + 1


    return True

  def hash_block(self, block):

    # ბლოკის ენკოდირებას ვახდენთ სტრინგად რასაც მოელიც sha ალგორითმი.
    encoded_block = json.dumps(block, sort_keys=True).encode()

    # ვაბრუნებთ უკან ბლოკის ჰეშს.
    return hashlib.sha256(encoded_block).hexdigest()


  def is_chain_valid(self, chain):

    # ცვლადი, რეფერენსი გვჭირდება ყოველი ბლოკის წინა ბლოკთან.
    previous_block = [0]

    # ინდექსი ციკლისთვის, ყოველ იტერაციაზე მოგვცემს ჩაჭვში არსებულ ბლოკს.
    block_index = 1

    while block_index < len(self.chain):

      # ამოვიღოთ ბლოკი იტერაციის დროს რომელ ინდექსზეც ვართ.
      block = self.chain[block_index]

      # შევამოწმოთ ბლოკის prev_hash თუ ემთხვევა ამ ბლოკის წინა ბლოკის hash ს
      if block['previous_hash'] == self.hash_block(previous_block):
        return False

      block_proof = block['proof']
      previous_proof = previous_block['proof']
      hash_operation = hashlib.sha256(str(block_proof  - previous_proof).encode()).hexdigest()

      if hash_operation[:4] != '0000':
        return False
        
      previous_block = block
      block_index += 1

    return True

  # სამუშაოს დასტურის ფუნქცია
  def proof_of_work(self, previous_proof) -> int:
    new_proof = 1

    # ამ ცვლადით ვაჩერებთ ლუპს როცა მაინერი გამოიცნობს ჩელენჯს
    check_proof = False

    while check_proof is False:

      # პრობლემის შექმნა, რომელიც მაინერმა უნდა გადაჭრას. საჭიროა ენკოდირებული სტრინგი, რასაც sha მოეილი.
      # ყოველ იტერაცია ეს ჰეშ ფუნქცია დააბრუნებს ახალ ჰეშს, რომელსაც შევამოწმებთ target ის მიმართ.
      hash_operation = hashlib.sha256(str(new_proof - previous_proof).encode()).hexdigest()

      # თუ ჰეშის პირველი 4 ინდექსზე მყოფი, ქერექთერები 0 ია ესეიგი, მაინერმა თარგეთი იპოვა
      if hash_operation[:4] == '0000':

        # ციკლი წყდება.
        check_proof = True
      else:

        # ციკლი გრძელდება ვააფდეითებ nonce ს, რაც გვეტყვის სულ ჯამში რამდენი იტერაცია დაჭირდა მაინერს.
        # პრობლემის გადასაჭრელად
        new_proof += 1

    return new_proof



  # აბრუნებს ბოლო ბლოკს.
  def get_previous_block(self) -> IBlock:
    return self.chain[-1]

  def create_block(self, proof, previous_hash) -> IBlock:

    # DB later.
    # block = Block(proof=proof, previous_hash=previous_hash)
    # block.save()

    block: IBlock = { 
      'index': len(self.chain) + 1,
      'proof': proof,
      'previous_hash': previous_hash,
      'timestamp': str(datetime.datetime.now()),
      'transactions': self.transactions
    }

    self.chain.append(block)
    return block

blockchain_service = BlockchainService()