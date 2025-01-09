from typing import Any, Optional
from langchain.schema.runnable import Runnable, RunnableConfig


class LogAndForward(Runnable):
    def invoke(self, input: Any, config: Optional[RunnableConfig] = None) -> Any:
        return input
