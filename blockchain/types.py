from pydantic import BaseModel
from typing import List, Optional

class ITransaction(BaseModel):
  sender: str
  receiver: str
  amount: int
  timestamp: str

class TransactionDto(BaseModel):
  sender: str
  receiver: str
  amount: int

class TransactionResponse(BaseModel):
  block: int
  message: str

class ConnectNodesDto(BaseModel):
  nodes: List[str]

class ConnectNodeRessponse(BaseModel):
  message: str
  nodes: List[str]

class IBlock(BaseModel):
  timestamp: str
  index: int
  proof: int
  previous_hash: str
  transactions: List[ITransaction]

class ReplaceChainResponse(BaseModel):
  message: str
  new_chain: Optional[List[IBlock]]
  old_chain: Optional[List[IBlock]]