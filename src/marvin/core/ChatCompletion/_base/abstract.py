from abc import ABC, abstractproperty


class AbstractChatRequest(ABC):
    pass


class AbstractChatResponse(ABC):
    @abstractproperty
    def messsage(self):
        pass

    @abstractproperty
    def function_call(self):
        pass

    @abstractproperty
    def finish_reason(self):
        pass

    def call_function(self):
        pass


class AbstractChatCompletionSettings(ABC):
    pass


class AbstractChatCompletion(ABC):
    pass


class AbstractConversationState(ABC):
    pass
