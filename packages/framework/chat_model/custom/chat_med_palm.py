import json
import os
from typing import Any, Dict, Iterator, List, Optional
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessageChunk, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult


class ChatMedPalm(BaseChatModel):
    """A custom chat model that uses Google's MedPalm model.

    This model uses the Google AI Platform to generate responses using the MedPalm model.

    Example:
        .. code-block:: python

            model = ChatMedPalm(project_id="your-project-id")
            result = model.invoke([HumanMessage(content="What are the symptoms of diabetes?")])
    """

    project_id: str
    """The Google Cloud project ID"""
    location: str = "us-central1"
    """The location of the AI Platform API endpoint"""
    model_name: str = "medlm-large"
    """The ID of the MedPalm model"""
    client: Any = None
    """The AI Platform client"""

    def __init__(self, **data):

        # Read the GOOGLE_APPLICATION_CREDENTIALS environment variable
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

        if credentials_path:
            with open(credentials_path, "r") as f:
                credentials = json.load(f)
                project_id = credentials.get("project_id")
                if project_id:
                    data["project_id"] = project_id
                else:
                    raise ValueError("Project ID not found in credentials")
        else:
            raise ValueError(
                "GOOGLE_APPLICATION_CREDENTIALS environment variable is not set"
            )

        super().__init__(**data)
        client_options = {"api_endpoint": f"{self.location}-aiplatform.googleapis.com"}
        self.client = aiplatform.gapic.PredictionServiceClient(
            client_options=client_options
        )

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        merged_messages = self._merge_messages(messages)
        instance_dict = {"content": merged_messages.content}
        instance = json_format.ParseDict(instance_dict, Value())
        instances = [instance]
        parameters_dict = {**kwargs}
        parameters = json_format.ParseDict(parameters_dict, Value())

        endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model_name}"
        response = self.client.predict(
            endpoint=endpoint,
            instances=instances,
            parameters=parameters,
        )

        predictions = response.predictions
        if predictions:
            # Handle MapComposite object
            prediction = dict(predictions[0])
            content = prediction.get("content", "")
        else:
            content = "No response generated."

        # Convert PredictResponse to a dictionary
        response_dict = {
            "predictions": [dict(pred) for pred in response.predictions],
            "metadata": dict(response.metadata) if response.metadata else {},
        }

        message = AIMessage(
            content=content,
            additional_kwargs={},
            response_metadata={"raw_response": response_dict},
        )

        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def _merge_messages(self, messages: List[BaseMessage]) -> BaseMessage:
        system_messages = []
        human_messages = []

        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_messages.append(str(msg.content))  # Ensure content is a string
            elif isinstance(msg, HumanMessage):
                human_messages.append(str(msg.content))  # Ensure content is a string
            elif isinstance(msg, AIMessage):
                raise ValueError("AI messages are not allowed for medPalm models.")

        # Use only strings in the join method
        merged_system = ". ".join(system_messages)
        merged_human = ". ".join(human_messages)

        return HumanMessage(
            content=f"your instructions:\n<{merged_system}>\nthe request:\n<{merged_human}>"
        )

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        # MedPalm doesn't support streaming, so we'll simulate it by yielding chunks
        result = self._generate(messages, stop, run_manager, **kwargs)
        content = result.generations[0].message.content

        # Ensure content is a string for AIMessageChunk
        if isinstance(content, str):
            for char in content:
                chunk = ChatGenerationChunk(message=AIMessageChunk(content=char))
                if run_manager:
                    run_manager.on_llm_new_token(char, chunk=chunk)
                yield chunk

    @property
    def _llm_type(self) -> str:
        return "medpalm"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "project_id": self.project_id,
            "location": self.location,
        }
