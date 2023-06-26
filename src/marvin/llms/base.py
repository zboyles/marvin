from abc import ABC, abstractmethod
from pydantic import BaseModel
from functools import wraps, partial
import asyncio

def api_route(func=None, **kwargs):
    if func is None:
        # The decorator was called with arguments. Return a new decorator function 
        # that can read the function to be decorated.
        return partial(api_route, **kwargs)
    else:
        if asyncio.iscoroutinefunction(func):
            # If function is a coroutine function, wrap it with an async wrapper
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await func(*args, **kwargs)
            wrapper = async_wrapper
        else:
            # If function is a regular function, wrap it with a regular wrapper
            @wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)

        wrapper.is_api_route = True
        wrapper.route_kwargs = kwargs
        return wrapper

class BaseLanguageModelConfig(BaseModel):
    pass

class BaseLanguageModel(ABC):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        cls.__api_routes__ = []
        for attr, value in cls.__dict__.items():
            func = value
            # Handle partials
            if isinstance(func, partial):
                func = func.func
            # Extract function if it's a property
            if isinstance(func, property):
                func = func.fget
            
            if getattr(func, 'is_api_route', False):
                cls.__api_routes__.append((attr, getattr(func, 'route_kwargs', {})))
            
    @abstractmethod
    async def acreate(self, *args, **kwargs):
        if hasattr(super(), 'acreate'):
            return await super().acreate(*args, **kwargs)
        raise NotImplementedError

    @abstractmethod
    def create(self, *args, **kwargs):
        if hasattr(super(), 'create'):
            return super().create(*args, **kwargs)
        raise NotImplementedError
    
    def attach(self, router, path: str = '/',  **route_kwargs):
        for route_name, route_kw in self.__api_routes__:
            route_func = getattr(self, route_name)
            route_defaults = {'endpoint': route_func, 'methods': ['GET'], 'name': route_name}
            router.add_api_route(path, **{**route_defaults, **route_kwargs, **route_kw})
        return None
    
