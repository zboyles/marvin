from abc import ABC, abstractmethod
from typing import Optional

from fastapi.routing import APIRouter


class DeploymentMixin:
    @property
    def app(self):
        from marvin.deployment import Deployment

        # TODO: This is a hack to avoid circular imports.
        return Deployment(
            component=self,
            app_kwargs=self._app_kwargs,
            router_kwargs=self._router_kwargs,
            uvicorn_kwargs=self._uvicorn_kwargs,
        ).app

    @property
    def router(self):
        from marvin.deployment import Deployment

        # TODO: This is a hack to avoid circular imports.
        return Deployment(component=self, router_kwargs=self._router_kwargs).router


class AIComponent(DeploymentMixin, ABC):
    """
    AIComponent is an abstract base class that defines the interface for all components.
    """

    _app_kwargs: Optional[dict] = None
    _router_kwargs: Optional[dict] = None
    _uvicorn_kwargs: Optional[dict] = None

    def __init__(
        self,
        *args,
        app_kwargs: Optional[dict] = None,
        router_kwargs: Optional[dict] = None,
        uvicorn_kwargs: Optional[dict] = None,
        **kwargs,
    ):
        self._app_kwargs = app_kwargs
        self._router_kwargs = router_kwargs
        self._uvicorn_kwargs = uvicorn_kwargs

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def description(self):
        pass

    @abstractmethod
    def setup_routes(self, router: APIRouter):
        pass
