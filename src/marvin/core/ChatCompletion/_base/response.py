from abc import ABC, abstractmethod, abstractproperty
from operator import itemgetter
from typing import Any, Callable

from marvin.pydantic import BaseModel


class AbstractChatResponse(ABC):
    def __iter__(self):
        return self.raw.__iter__()

    def __next__(self):
        return self.raw.__next__()

    @abstractproperty
    def messsage(self):
        """
        Returns the message most recently sent to the user.
        """
        pass

    @abstractproperty
    def function_call(self):
        """
        Returns the function and arguments to call, if any.
        """
        pass

    @abstractproperty
    def finish_reason(self):
        """
        Returns the reason the conversation finished.
        """
        pass

    @abstractproperty
    def tokens(self):
        """
        Returns the reason the conversation finished.
        """
        pass

    @abstractmethod
    def call_function(self):
        """
        Calls the function with the arguments.
        """
        pass


class BaseChatResponse(BaseModel, AbstractChatResponse):
    raw: Any
    __request__: Any

    def __getattr__(self, name):
        """
        This method attempts to get the attribute from the raw response.
        If it doesn't exist, it falls back to the standard attribute access.
        """
        try:
            return getattr(self.raw, name)
        except AttributeError:
            return self.__getattribute__(name)

    @property
    def callables(self):
        """
        This property returns a list of all callable functions from the request.
        """
        return [x for x in self.request.functions if isinstance(x, Callable)]

    @property
    def callable_registry(self):
        """
        This property returns a dictionary mapping function names to functions for all
        callable functions from the request.
        """
        return {fn.__name__: fn for fn in self.callables}

    @property
    def message(self):
        return None

    @property
    def function_call(self):
        return None

    def call_function(self, as_message=True):
        """
        This method evaluates the function call in the response and returns the result.
        If as_message is True, it returns the result as a function message.
        Otherwise, it returns the result directly.
        """
        if not self.function_call:
            return None
        name, raw_arguments = itemgetter("name", "arguments")(self.function_call)
        function = self.callable_registry.get(name)
        arguments = function.model.parse_raw(raw_arguments)
        value = function(**arguments.dict(exclude_none=True))
        if as_message:
            return {"role": "function", "name": name, "content": value}
        else:
            return value

    def to_model(self):
        """
        This method parses the function call arguments into the response model and
        returns the result.
        """
        return self.request._response_model.parse_raw(self.function_call.arguments)
