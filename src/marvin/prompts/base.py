from pydantic import BaseModel, validator
from typing import Optional 
from jinja2 import Template

from abc import ABC, abstractmethod

class BasePrompt(BaseModel, ABC):     
    
    template: Optional[str] = None

    @validator('template', pre = True)
    def populate_template_from_docstring_if_absent(cls, value): 
        if not value and cls.__doc__:
            return(cls.__doc__)
        return value
    
    @abstractmethod
    def render(self, *args, **kwargs):
        if not self.template:
            raise NotImplementedError("No template to render!")
        return(Template(self.template).render(self.dict(*args, **kwargs)))