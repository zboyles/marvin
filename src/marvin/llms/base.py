from pydantic import BaseModel
from abc import ABC, abstractmethod

class BaseLanguageModel(BaseModel, ABC):
    
    async def acreate(self, *args, **kwargs):
        return super().acreate(*args, **kwargs)
    
    def create(self, *args, **kwargs):
        return super().create(*args, **kwargs)
    
