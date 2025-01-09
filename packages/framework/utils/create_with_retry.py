from typing import Optional, Callable, cast
from langchain.prompts import ChatPromptTemplate


def create_with_retry(
    retry: Optional[int] = 3,
) -> Callable[[ChatPromptTemplate], ChatPromptTemplate]:
    return lambda template: cast(
        ChatPromptTemplate,
        template.with_retry(stop_after_attempt=retry if retry is not None else 3),
    )
