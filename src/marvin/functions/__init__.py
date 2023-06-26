from functools import partial, wraps
from inspect import iscoroutinefunction, signature

from fastapi import APIRouter
from marvin.utils.pydantic import function_to_json_schema


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