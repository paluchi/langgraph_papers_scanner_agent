from typing import Any
from langchain.chat_models.base import BaseChatModel
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

from packages.framework.utils.parse_and_convert import parse_and_convert
from packages.framework.utils.create_with_partial import create_with_partial


def create_generic_chain(
    chat_model: BaseChatModel,
    template: str,
    pydantic_class: Any = None,  # Make pydantic_class optional
    **kwargs: Any,
) -> ChatPromptTemplate:

    generic_prompt_template = ChatPromptTemplate.from_template(template)

    # Choose the parser based on whether pydantic_class is provided
    parser = (
        PydanticOutputParser(pydantic_object=pydantic_class)
        if pydantic_class
        else StrOutputParser()
    )
    parser_format_instructions = (
        parser.get_format_instructions() if pydantic_class else ""
    )

    # Create the partial function with the given context and format instructions
    with_partial = create_with_partial(
        format_instructions=parser_format_instructions,
        **kwargs,
    )

    # Return the chain with optional parse_and_convert depending on pydantic_class
    if pydantic_class:
        # Use parse_and_convert if the result is a Pydantic model
        return (
            with_partial(generic_prompt_template)
            | chat_model
            | parser
            | parse_and_convert
        )
    else:
        # If it's a string parser, no need for parse_and_convert
        return with_partial(generic_prompt_template) | chat_model | parser
