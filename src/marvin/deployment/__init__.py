import asyncio
from typing import Union, Optional

import uvicorn
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel, Extra

from marvin.utilities.types import safe_issubclass
from marvin.components.ai_component import AIComponent

import inspect


class Deployment(BaseModel):
    """
    Deployment class handles the deployment of AI applications, models or functions.
    """

    def __init__(
        self,
        component: AIComponent,
        *args,
        app_kwargs: Optional[dict] = None,
        router_kwargs: Optional[dict] = None,
        uvicorn_kwargs: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.app = FastAPI(**(app_kwargs or {}))
        self.router = APIRouter(**(router_kwargs or {}))
        self.component = component
        self._mount_router()
        self.app.include_router(self.router)
        self._uvicorn_kwargs = {
            "app": self.app,
            "host": "0.0.0.0",
            "port": 8000,
            **(uvicorn_kwargs or {}),
        }

    def __call__(self):
        return self.app

    def _mount_router(self):
        self.component.setup_routes(self.router)

    def serve(self):
        """
        Serves the FastAPI app.
        """
        try:
            config = uvicorn.Config(**(self._uvicorn_kwargs or {}))
            server = uvicorn.Server(config)
            loop = asyncio.get_event_loop()
            loop.run_until_complete(server.serve())
        except Exception as e:
            print(f"Error while serving the application: {e}")
            raise e

    class Config:
        extra = Extra.allow
