

from fastapi.routing import APIRouter
from typing import Union, Optional

from marvin.agents.utils import resolve_router, add_base_router
from marvin.prompts.base import BasePrompt
from marvin.llms.base import BaseLanguageModel

class Agent:
    def __init__(
            self, 
            prompt: Optional[BasePrompt] = None,
            language_model: BaseLanguageModel = None,
            router: Optional[APIRouter] = None, 
            tools: Optional[APIRouter] = None,
        ):
        self._router = resolve_router(router)
        self.function_router = resolve_router(tools) 
        self.function_router.add = self.function_router.post
        self.prompt = prompt or BasePrompt()
        self.language_model = language_model
        add_base_router(self.router, getattr(self.language_model, "aquery", None))

    @property
    def router(self):
        self._router.include_router(self.function_router, prefix = '/tools')
        return(self._router)
        
    @property
    def functions(self):
        # Duplicate of tools, since naming conventions are different.
        return(self.router)
        
    @property
    def tools(self):
        # Duplicate of functions, since naming conventions are different.
        return(self.function_router)
    
    @property
    def render(self):
        return(self.prompt.render)