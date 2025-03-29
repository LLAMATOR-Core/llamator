import logging
from typing import Dict, List, Optional

from langchain.schema import BaseMessage
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs.llm_result import LLMResult
from openai import OpenAI

from .chat_client import ClientBase
from .langchain_integration import get_langchain_chat_models_info

logger = logging.getLogger(__name__)

# Introspect langchain for supported models
chat_models_info = get_langchain_chat_models_info()


class FakeChatClient(ClientBase):
    def interact(self, history: List[Dict[str, str]], messages: List[Dict[str, str]]) -> Dict[str, str]:
        return {"role": "assistant", "content": "FakeChat response"}


class ClientLangChain(ClientBase):
    """
    Wrapper for interacting with models through LangChain.

    Parameters
    ----------
    backend : str
        The backend name to use for model initialization.
    system_prompts : Optional[List[str]]
        List of system prompts for initializing the conversation context (optional).
    **kwargs
        Additional arguments passed to the model's constructor.

    Methods
    -------
    _convert_to_base_format(message: BaseMessage) -> Dict[str, str]
        Converts a LangChain message (HumanMessage, AIMessage) to the base format (Dict with "role" and "content").

    _convert_to_langchain_format(message: Dict[str, str]) -> BaseMessage
        Converts a message from the base format (Dict) to LangChain's format (HumanMessage, AIMessage).

    interact(history: List[Dict[str, str]], messages: List[Dict[str, str]]) -> Dict[str, str]
        Takes conversation history and new messages, sends a request to the model, and returns the response as a dictionary.
    """

    def __init__(
        self,
        backend: str,
        system_prompts: Optional[List[str]] = None,
        model_description: Optional[str] = None,
        **kwargs,
    ):
        chat_models_info = get_langchain_chat_models_info()
        if backend in chat_models_info:
            self.client = chat_models_info[backend].model_cls(**kwargs)
        else:
            raise ValueError(
                f"Invalid backend name: {backend}. Supported backends: {', '.join(chat_models_info.keys())}"
            )

        self.system_prompts = system_prompts
        self.model_description = model_description

    @staticmethod
    def _convert_to_langchain_format(message: Dict[str, str]) -> BaseMessage:
        """
        Converts a message from the base format (Dict) to LangChain's format.

        Parameters
        ----------
        message : Dict[str, str]
            A message in the base format (Dict with "role" and "content") to convert.

        Returns
        -------
        BaseMessage
            The message in LangChain format (HumanMessage, AIMessage, or SystemMessage).
        """
        if message["role"] == "user":
            return HumanMessage(content=message["content"])
        elif message["role"] == "assistant":
            return AIMessage(content=message["content"])
        elif message["role"] == "system":
            return SystemMessage(content=message["content"])
        else:
            raise ValueError(f"Unsupported role: {message['role']}")

    @staticmethod
    def _convert_to_base_format(message: BaseMessage) -> Dict[str, str]:
        """
        Converts a LangChain message (HumanMessage, AIMessage) to the base format.

        Parameters
        ----------
        message : BaseMessage
            A message in LangChain format to convert.

        Returns
        -------
        Dict[str, str]
            The message in base format with "role" and "content".
        """
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, AIMessage):
            role = "assistant"
        elif isinstance(message, SystemMessage):
            role = "system"
        else:
            raise ValueError(f"Unsupported message type: {type(message)}")

        return {"role": role, "content": str(message.content)}

    def interact(self, history: List[Dict[str, str]], messages: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Takes conversation history and new messages, sends a request to the model, and returns the response.

        Parameters
        ----------
        history : List[Dict[str, str]]
            The conversation history.

        messages : List[Dict[str, str]]
            New messages to be processed.

        Returns
        -------
        Dict[str, str]
            The response from the model in dictionary format with "role" and "content".
        """
        # Convert history and messages to LangChain format
        langchain_history = [self._convert_to_langchain_format(msg) for msg in history]
        langchain_messages = [self._convert_to_langchain_format(msg) for msg in messages]

        # Combine history and messages
        combined_messages = langchain_history + langchain_messages

        try:
            # Use the newer invoke_with_message_history API if available
            if hasattr(self.client, "invoke"):
                response = self.client.invoke(combined_messages)
                if isinstance(response, BaseMessage):
                    response_message = response
                else:
                    # If the response is not a BaseMessage, assume it's content that needs to be wrapped
                    response_message = AIMessage(content=str(response))
            # Fall back to generate API for older versions
            elif hasattr(self.client, "generate"):
                llm_result: LLMResult = self.client.generate(messages=combined_messages)
                response_message = AIMessage(content=llm_result.generations[0][0].text)
            else:
                raise RuntimeError("LangChain client has no supported method for generating responses")
        except Exception as e:
            raise RuntimeError(f"Chat inference failed with error: {e}")

        return self._convert_to_base_format(response_message)


class ClientOpenAI(ClientBase):
    """
    Wrapper for interacting with OpenAI-compatible API.
    This client can be used to interact with any language model that supports the OpenAI API, including but not limited to OpenAI models.

    Parameters
    ----------
    api_key : str
        The API key for authentication.
    base_url : str
        The base URL of the OpenAI-compatible API.
    model : str
        The model identifier to use for generating responses.
    temperature : float
        The temperature setting for controlling randomness in the model's responses.
    system_prompts : Optional[List[str]]
        List of system prompts for initializing the conversation context (optional).
    model_description : str
        Description of the model, including domain and other features (optional).

    Methods
    -------
    _convert_to_base_format(message: Dict[str, str]) -> Dict[str, str]
        Converts a message from OpenAI format (Dict) to the base format (Dict with "role" and "content").

    _convert_to_openai_format(message: Dict[str, str]) -> Dict[str, str]
        Converts a message from the base format (Dict with "role" and "content") to OpenAI's format (Dict).

    interact(history: List[Dict[str, str]], messages: List[Dict[str, str]]) -> Dict[str, str]
        Takes conversation history and new messages, sends a request to the OpenAI-compatible API, and returns the response.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        temperature: float = 0.1,
        system_prompts: Optional[List[str]] = None,
        model_description: Optional[str] = None,
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature
        self.system_prompts = system_prompts
        self.model_description = model_description

    @staticmethod
    def _convert_to_base_format(message: Dict[str, str]) -> Dict[str, str]:
        """
        Converts a message from OpenAI format to the base format.

        Parameters
        ----------
        message : Dict[str, str]
            A message in OpenAI format to convert.

        Returns
        -------
        Dict[str, str]
            The message in base format with "role" and "content".
        """
        return {"role": message["role"], "content": message["content"]}

    @staticmethod
    def _convert_to_openai_format(message: Dict[str, str]) -> Dict[str, str]:
        """
        Converts a message from base format (Dict) to OpenAI format.

        Parameters
        ----------
        message : Dict[str, str]
            A message in the base format (Dict with "role" and "content") to convert.

        Returns
        -------
        Dict[str, str]
            The message in OpenAI format.
        """
        return {"role": message["role"], "content": message["content"]}

    def interact(self, history: List[Dict[str, str]], messages: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Takes conversation history and new messages, sends a request to the OpenAI-compatible API, and returns the response.

        Parameters
        ----------
        history : List[Dict[str, str]]
            The conversation history.

        messages : List[Dict[str, str]]
            New messages to be processed.

        Returns
        -------
        Dict[str, str]
            The response from the model in dictionary format with "role" and "content".
        """
        # Convert history and new messages to OpenAI format
        openai_history = [self._convert_to_openai_format(msg) for msg in history]
        openai_messages = [self._convert_to_openai_format(msg) for msg in messages]

        # Add new messages to the history
        openai_history += openai_messages

        try:
            # Send the history to the model and get the result
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=openai_history,
                temperature=self.temperature,
            )
            # Extract the response text from the API
            response_content = completion.choices[0].message.content
            response_message = {"role": "assistant", "content": response_content}
        except Exception as e:
            logger.warning(f"Chat inference failed with error: {e}")
            raise

        # Convert the response to base format
        return self._convert_to_base_format(response_message)
