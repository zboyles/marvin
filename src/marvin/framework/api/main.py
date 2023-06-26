from fastapi import FastAPI
from marvin.agents.base import Agent 
from marvin.llms.openai import ChatCompletion

app = FastAPI()

@app.get("/")
def index():
    return {"message": "Hello World!"}

agent = Agent(
    language_model = ChatCompletion()
)

@agent.tools.get(path = '/add')
def add(x: int, y:int) -> int:
    '''Adds two functions'''
    return(x+y)

@agent.tools.get(path = '/subtract')
def substract(x: int, y:int) -> int:
    return(x-y)

@agent.tools.post(path = '/multiply')
def multiply(x: int, y:int) -> int:
    return(x*y)

app.include_router(agent.router)