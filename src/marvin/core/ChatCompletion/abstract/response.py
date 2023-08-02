from abc import ABC, abstractmethod, abstractproperty
from operator import itemgetter
from typing import Callable, Type

from marvin.pydantic import BaseModel, validate_arguments


class AbstractChatResponse(BaseModel, ABC):
    raw: Type[BaseModel]
    request: Type[BaseModel]
    function_registry: dict[str, Callable] = None
    response_model: Type[BaseModel] = None

    def __iter__(self):
        return self.raw.__iter__()

    def __next__(self):
        return self.raw.__next__()

    def __repr__(self):
        return self.raw.__repr__()

    def __getattr__(self, name):
        """
        This method attempts to get the attribute from the raw response.
        If it doesn't exist, it falls back to the standard attribute access.
        """
        try:
            return getattr(self.raw, name)
        except AttributeError:
            return self.__getattribute__(name)

    @abstractproperty
    def messsage(self):
        """
        Returns the message most recently sent to the user.
        """
        pass

    @abstractproperty
    def finish_reason(self):
        """
        Returns the reason the conversation finished.
        """
        pass

    @abstractmethod
    def function_call(self) -> dict[str, str]:
        """
        Returns the function and arguments to call, if any.
        """
        pass

    def call_function(self, *args, as_value=False, **kwargs):
        """
        Calls the function with the arguments.
        """
        function_call = self.function_call(*args, **kwargs)

        if not function_call:
            return None

        fn_name, fn_raw_arguments = itemgetter("name", "arguments")(function_call)

        fn = self.function_registry.get(fn_name)
        fn_arguments = validate_arguments(fn).model.parse_raw(fn_raw_arguments)

        value = fn(**fn_arguments.dict(exclude_none=True))

        if as_value:
            return value
        else:
            return {"role": "function", "name": fn_name, "content": value}

    def parse_raw(self, *args, **kwargs):
        """
        This method parses the raw response and returns the result.
        """
        return self.response_model.parse_raw(*args, **kwargs)

    def to_model(self):
        """
        This method parses the function call arguments into the response model and
        returns the result.
        """
        return self.to_model(self.function_call())
