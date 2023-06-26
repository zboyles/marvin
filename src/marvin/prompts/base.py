from pydantic import BaseModel, root_validator 
from jinja2 import Template

class BasePrompt(BaseModel):
    'All Prompts that Inherit from BasePrompt use their docstring to prompt.'

    def render(self, seperator = '\n', **kwargs):
        return(Template(f'{seperator}'.join([
            getattr(subclass, '__doc__') or '' for subclass in self.get_inherited_prompts()
        ])).render(self.dict(**kwargs)))
    
    def get_inherited_prompts(self) -> str:
        """
        Function to get the inherited prompts
        """
        return list(filter(
            lambda cls: (
                issubclass(cls, BasePrompt)
            )
        , self.__class__.__mro__))[1::-1]
    
