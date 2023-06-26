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