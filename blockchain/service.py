
import json
import datetime
import hashlib

from db.conn import db
from .models import Block


class BlockchainService:

  def __init__(self):
    self.chain = []
    
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

  def proof_of_work(self, previous_proof):
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



  def get_previous_block(self):
    return self.chain[-1]

  def create_block(self, proof, previous_hash):

    block = Block(
      proof=proof,
      previous_hash=previous_hash
    )

    block.save()

    block = {
      'proof': proof,
      'previous_hash': previous_hash
    }

    return block

blockchain_service = BlockchainService()