from typing import Dict, Optional
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from packages.framework.utils.create_with_partial import create_with_partial
from packages.framework.utils.parse_and_convert import parse_and_convert
from langchain.prompts import ChatPromptTemplate
from packages.framework.chat_model.get_chat_model import get_chat_model

# HERE LIES A HELPER METHOD TO INTERACT WITH THE LLM
# --------------------------------------------------


GEMINI_FLASH_1_5 = get_chat_model("gemini-1.5-flash-002")


def call_llm(
    prompt_template: ChatPromptTemplate,
    input_parameters: Optional[Dict[str, str]],
    pydantic_object,
    llm=GEMINI_FLASH_1_5,
):
    params = input_parameters or {}
    parser = (
        PydanticOutputParser(pydantic_object=pydantic_object)
        if pydantic_object
        else None
    )
    with_partial_inputs = create_with_partial(**params)
    chain = (
        with_partial_inputs(
            prompt_template,
            format_instructions=(parser.get_format_instructions() if parser else None),
        )
        | llm
        | parser
        | parse_and_convert
    )

    result = chain.invoke({})
    return result
