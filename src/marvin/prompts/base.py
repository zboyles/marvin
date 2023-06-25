from pydantic import BaseModel, root_validator 
from jinja2 import Template

class BasePrompt(BaseModel):         
    template: str

    @root_validator(pre = True)
    def populate_template_from_docstring_if_absent(cls, values): 
        if not values.get('template') and cls.__doc__:
            values['template'] = cls.__doc__
        return values
    
    def render(self, *args, **kwargs):
        if not self.template:
            raise NotImplementedError("No template to render!")
        return(Template(self.template).render(self.dict(*args, **kwargs)))