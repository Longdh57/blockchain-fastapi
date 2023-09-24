import uvicorn

from uuid import uuid4
from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from blockchain import blockchain
from config import settings
from shemas.sche_base import DataResponse

node_identifier = str(uuid4()).replace('-', '')


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME, openapi_url=f'/openapi.json',
        docs_url=f'/docs', redoc_url=None,
        description='Simple Blockchain',
        debug=settings.DEBUG
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    return application


app = get_application()


@app.get("/mine", response_model=DataResponse)
def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return DataResponse().success_response(data=response)


class NewTransactionRequest(BaseModel):
    sender: str
    recipient: str
    amount: float


@app.post('/transactions/new', response_model=DataResponse)
def new_transaction(req_data: NewTransactionRequest):
    index = blockchain.new_transaction(req_data.sender, req_data.recipient, req_data.amount)
    response = {'message': f'Transaction will be added to Block {index}'}
    return DataResponse().success_response(data=response)


@app.get('/chain', response_model=DataResponse)
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return DataResponse().success_response(data=response)


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
