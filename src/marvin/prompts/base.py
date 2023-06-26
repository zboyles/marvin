from enum import Enum
from typing import Optional

from jinja2 import Template
from pydantic import BaseModel


class Role(Enum):
    system = 'system'
    assistant = 'assistant'
    user = 'user'

class Message(BaseModel):
    role: Role = Role.system.value
    content: str

class BasePrompt(BaseModel):
    'All Prompts that Inherit from BasePrompt use their docstring to prompt.'
    
    history: Optional[list[Message]] = []

    def render(self, seperator = '\n', **kwargs) -> str:
        return(Template(f'{seperator}'.join([
            getattr(subclass, '__doc__') or '' for subclass in self.get_inherited_prompts()
        ])).render(self.dict(**kwargs)))
    
    def system_message(self, seperator = '\n', **kwargs) -> Message:
        return(Message( role = 'system', content = self.render(seperator, **kwargs)))

    def messages(self, as_dict = False) -> list[Message]:
        messages = [self.system_message(), *self.history]
        if as_dict:
            messages = [x.dict() for x in messages]
        return messages
    
    def query(self, q: str):
        return self.__class__(history = self.history + [
            Message(role = 'user', content = q)
        ])
    
    def get_inherited_prompts(self) -> str:
        """
        Function to get the inherited prompts
        """
        return list(filter(
            lambda cls: (
                issubclass(cls, BasePrompt)
            )
        , self.__class__.__mro__))[::-1][1:]