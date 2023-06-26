

from typing import Optional

from fastapi.routing import APIRouter
from marvin.agents.utils import resolve_router
from marvin.llms.base import BaseLanguageModel
from marvin.prompts.base import BasePrompt
from marvin.utils.pydantic import function_to_json_schema


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
        self.language_model.attach(self._router)

    @property
    def router(self):
        self._router.include_router(self.function_router, prefix = '/tools')
        return(self._router)
        
    @property
    def tools(self):
        return(self.function_router)
        
    @property
    def functions(self):
        return([
            function_to_json_schema(route.endpoint) 
            for route in self.function_router.routes
        ])
    
    @property
    def render(self):
        return(self.prompt.render)