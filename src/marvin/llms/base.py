from pydantic import BaseModel
from abc import ABC, abstractmethod

class BaseLanguageModelConfig(BaseModel):
    pass

class BaseLanguageModel(BaseModel, ABC):

    prompt_config: BaseLanguageModelConfig
    
    async def acreate(self, *args, **kwargs):
        return super().acreate(*args, **kwargs)
    
    def create(self, *args, **kwargs):
        return super().create(*args, **kwargs)
    
