from functools import partial, wraps
from inspect import iscoroutinefunction, signature

from fastapi import APIRouter
from typing import Any, Callable
import inspect
from pydantic import create_model


def function_to_schema(function: Callable[..., Any], name: str = None) -> dict:
    """
    Converts a function's arguments into an OpenAPI schema by parsing it into a
    Pydantic model. To work, all arguments must have valid type annotations.
    """
    signature = inspect.signature(function)

    fields = {
        p: (
            signature.parameters[p].annotation,
            (
                signature.parameters[p].default
                if signature.parameters[p].default != inspect._empty
                else ...
            ),
        )
        for p in signature.parameters
        if p != getattr(function, "__self__", None)
    }

    # Create Pydantic model
    try:
        Model = create_model(name or function.__name__, **fields)
        Model.__doc__ = function.__doc__
    except RuntimeError as exc:
        if "see `arbitrary_types_allowed` " in str(exc):
            raise ValueError(
                f"Error while inspecting {function.__name__} with signature"
                f" {signature}: {exc}"
            )
        else:
            raise

    return Model.schema()

def function_to_json_schema(function: Callable[..., Any], name: str = None) -> dict:
    output = {}
    schema = function_to_schema(function)
    output['name'] = schema.pop('title')
    output['description'] = schema.pop('description', '')
    output['parameters'] = schema
    return(output)

class FunctionRegistry(APIRouter):
    def __init__(self):
        super().__init__()
        self.add = self.post

    @property
    def functions(self):
        return([
            function_to_json_schema(route.endpoint) 
            for route in self.function_router.routes
        ])
    
    def register(self, *args, **route_kwargs):
        def decorator(func):
            original_func = func
            # Handle partials by getting the original function
            if isinstance(original_func, partial):
                original_func = original_func.func

            # Check if function is a coroutine function
            if iscoroutinefunction(original_func):
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

            # Store the function signature for later
            wrapper.signature = signature(original_func)

            # Register the function with additional route kwargs
            self.add_api_route('/' + func.__name__, endpoint=wrapper)
            
            return wrapper

        # If register is used as a decorator without parentheses
        if args and callable(args[0]):
            func = args[0]
            return decorator(func)

        # If register is used as a decorator with parentheses
        return decorator