from marvin.llms.base import BaseLanguageModelConfig, BaseLanguageModel, api_route
import openai
from pydantic import BaseModel


class ChatCompletionConfig(BaseLanguageModelConfig):
    pass

class Message(BaseModel):
    role: str
    message: str

class ChatCompletion(BaseLanguageModel, openai.ChatCompletion):

    @api_route(path = '/')
    def acreate(self, message: list[Message]) -> str:
        return('nice')
    
    @api_route
    def create(self, message: list[Message]) -> str:
        return('nice')