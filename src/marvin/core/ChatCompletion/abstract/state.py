from abc import ABC
from typing import Type

from marvin.core.ChatCompletion.abstract.chat_completion import AbstractChatCompletion
from marvin.core.ChatCompletion.abstract.response import AbstractChatResponse
from marvin.pydantic import (
    BaseModel,
    Extra,
    Field,
)


class AbstractConversationState(BaseModel, ABC):
    """
    Placeholder for conversation state.
    """

    model: Type[AbstractChatCompletion] = Field(..., exclude=True)
    turns: list[AbstractChatResponse] = Field(default_factory=list)

    def __init__(self, model, *args, **kwargs):
        super().__init__(__model__=model, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    @property
    def last_response(self):
        return next(iter(self.turns[::-1]), None)

    @property
    def last_response(self):
        return next(iter(self.turns[::-1]), None)

    def create(self, *args, **kwargs):
        response = self.model.create(*args, **kwargs)
        self.turns.append(response)
        return response

    async def acreate(self, *args, **kwargs):
        response = await self.model.acreate(*args, **kwargs)
        self.turns.append(response)
        return response

    def push(self, *args, **kwargs):
        if self.turns:
            kwargs["messages"] = [
                *self.turns[-1].request.messages,
                self.turns[-1].raw.choices[0].message,
                *kwargs.get("messages", []),
            ]
        response = self.model.create(*args, **kwargs)
        self.turns.append(response)
        return response

    async def apush(self, *args, **kwargs):
        response = await self.model.acreate(*args, **kwargs)
        self.turns.append(response)
        return response

    class Config:
        extra = Extra.allow
        arbitrary_types_allowed = True
