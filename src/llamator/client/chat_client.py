import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from .langchain_integration import get_langchain_chat_models_info

logger = logging.getLogger(__name__)

# Introspect langchain for supported models
chat_models_info = get_langchain_chat_models_info()


class ClientBase(ABC):
    """
    Base class for interacting with chat models.
    The history and new messages are passed as a list of dictionaries.

    Attributes
    ----------
    system_prompts : Optional[List[str]]
        Optional system prompts to guide the conversation.
    model_description : Optional[str]
        Optional model description to guide the conversation.

    Methods
    -------
    interact(history: List[Dict[str, str]], messages: List[Dict[str, str]]) -> Dict[str, str]
        Takes the conversation history and new messages, sends them to the LLM, and returns a new response.
    """

    # Attributes that can be None by default
    system_prompts: Optional[List[str]] = None
    model_description: Optional[str] = None

    @abstractmethod
    def interact(self, history: List[Dict[str, str]], messages: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Takes the conversation history and new messages, sends them to the LLM, and returns a new response.

        Parameters
        ----------
        history : List[Dict[str, str]]
            A list of past messages representing the conversation history.

        messages : List[Dict[str, str]]
            A list of new messages to be sent to the LLM.

        Returns
        -------
        Dict[str, str]
            The response from the LLM in dictionary format, with "role" and "content" fields.
        """
        pass


class ChatSession:
    """
    Maintains a single conversation session, including the history, and supports optional system prompts.

    Attributes
    ----------
    client : ClientBase
        The client responsible for interacting with the LLM.

    system_prompts : List[Dict[str, str]]
        A list of system prompts used to initialize the conversation (if any).

    history : List[Dict[str, str]]
        The conversation history, containing both user and assistant messages.

    use_history : bool
        Determines whether to use the existing conversation history.
        If False, only the system prompts and the current user prompt are used.
        Defaults to True.

    strip_client_responses : bool
        Determines whether to strip space, tab, new line, [, ], <, >, \", ' from the start and end of the Client response.
        Defaults to True.

    Methods
    -------
    say(user_prompt: str, use_history: bool = True) -> Optional[str]
        Sends a user message to the LLM, updates the conversation history, and returns the assistant's response.

    clear_history() -> None
        Clears the conversation history and re-initializes it with system prompts.
    """

    def __init__(
        self,
        client: ClientBase,
        system_prompts: Optional[List[str]] = None,
        use_history: Optional[bool] = True,
        strip_client_responses: Optional[bool] = True,
    ):
        """
        Initializes the ChatSession with a client and optional system prompts.

        Parameters
        ----------
        client : ClientBase
            The client that handles interaction with the LLM.

        system_prompts : List[str], optional
            A list of system prompts to guide the conversation from the start.

        use_history : bool, optional
            Determines whether to use the existing conversation history.
            If False, only the system prompts and the current user prompt are used.
            Defaults to True.

        strip_client_responses : bool, optional
            Determines whether to strip space, tab, new line, [, ], <, >, \", ' from the start and end of the Client response.
            Defaults to True.
        """
        self.client = client
        self.use_history = use_history
        if system_prompts:
            self.system_prompts = [
                {"role": "system", "content": system_prompt_text} for system_prompt_text in system_prompts
            ]
        else:
            self.system_prompts = []
        # Initialize history with system prompts
        self.history = list(self.system_prompts)
        self.strip_client_responses = strip_client_responses

    def say(self, user_prompt: str) -> Optional[str]:
        """
        Sends a user message to the LLM, updates the conversation history based on the use_history flag,
        and returns the assistant's response.

        Parameters
        ----------
        user_prompt : str
            The user's message to be sent to the LLM.

        Returns
        -------
        Optional[str]
            The response from the assistant (LLM) as a string or None in case of exception.
        """
        logger.debug(f"say: system_prompts={self.system_prompts}")
        logger.debug(f"say: prompt={user_prompt}")

        # Interact with the LLM
        try:
            result = self.client.interact(
                history=self.history if self.use_history else list(self.system_prompts),
                messages=[{"role": "user", "content": user_prompt}],
            )
            if self.strip_client_responses:
                result["content"] = result["content"].strip(" \t\n[]<>\"'`")
            logger.debug(f"say: result={result}")
        except Exception as e:
            logger.error(f"say: {e}")
            self.history.append({"role": "user", "content": user_prompt})
            self.history.append({"role": "assistant", "content": ""})
            return None

        self.history.append({"role": "user", "content": user_prompt})
        self.history.append(result)

        return result["content"]

    def clear_history(self) -> None:
        """
        Clears the conversation history and re-initializes it with system prompts.
        """
        self.history = list(self.system_prompts)


class MultiStageInteractionSession:
    """
    Manages a multi-stage interaction between attacker and tested chat clients.

    Attributes
    ----------
    attacker_session : ChatSession
        The session for the attacker.
    tested_client_session : ChatSession
        The session for the tested client.
    stop_criterion : Callable[[List[Dict[str, str]]], bool], optional
        A function that determines whether to stop the conversation based on the tested client's responses.
    history_limit : int, optional
        The maximum allowed history length for the attacker.
    tested_client_response_handler : Callable[..., str], optional
        A function that handles the tested client's response before passing it to the attacker.
    attacker_response_separator : str, optional
        Separator for splitting the attacker's request into a reasoning part and a direct request.
        Only the direct request is sent to the tested client.
    current_step : int
        The current step of the attacker.
    refine_args : tuple
        Additional positional arguments for tested_client_response_handler.
    refine_kwargs : dict
        Additional keyword arguments for tested_client_response_handler.

    Methods
    -------
    start_conversation(start_prompt: str) -> Optional[bool]
        Starts the conversation using the attacker and alternates between attacker and tested client until a stopping condition is met.
    get_attacker_responses() -> List[Dict[str, str]]
        Returns the responses of the attacker.
    get_tested_client_responses() -> List[Dict[str, str]]
        Returns the responses of the tested client.
    get_current_step() -> int
        Returns the current step of the attacker.
    """

    def __init__(
        self,
        attacker_session: ChatSession,
        tested_client_session: ChatSession,
        stop_criterion: Optional[Callable[[List[Dict[str, str]]], bool]] = None,
        history_limit: Optional[int] = 20,
        tested_client_response_handler: Optional[Callable[..., str]] = None,
        attacker_response_separator: Optional[str] = None,
        refine_args: Optional[tuple] = None,
        refine_kwargs: Optional[dict] = None,
    ):
        """
        Initializes the MultiStageInteractionSession.

        Parameters
        ----------
        attacker_session : ChatSession
            The session for the attacker.
        tested_client_session : ChatSession
            The session for the tested client.
        stop_criterion : Callable[[List[Dict[str, str]]], bool]], optional
            A function that takes the tested client's history and returns True if the conversation should stop.
            If None, a default criterion that always returns False is used. (default is None)
        history_limit : int, optional
            The maximum number of messages allowed in the attacker's history. (default is 20)
        tested_client_response_handler : Callable[..., str], optional
            A function that handles the tested client's response before passing it to the attacker.
            If None, a default function that returns the response unchanged is used. (default is None)
        attacker_response_separator : str, optional
            Separator for splitting the attacker's request into a reasoning part and a direct request.
            Only the direct request is sent to the tested client.
        refine_args : tuple, optional
            Additional positional arguments for tested_client_response_handler. (default is None)
        refine_kwargs : dict, optional
            Additional keyword arguments for tested_client_response_handler. (default is None)
        """
        self.attacker_session = attacker_session
        self.tested_client_session = tested_client_session
        self.stop_criterion = stop_criterion if stop_criterion is not None else self.default_stop_criterion
        self.history_limit = history_limit
        self.tested_client_response_handler = (
            tested_client_response_handler
            if tested_client_response_handler is not None
            else self.default_tested_client_response_handler
        )
        self.attacker_response_separator = attacker_response_separator
        self.current_step = 1
        self.refine_args = refine_args if refine_args is not None else ()
        self.refine_kwargs = refine_kwargs if refine_kwargs is not None else {}

    @staticmethod
    def default_stop_criterion(tested_client_history: List[Dict[str, str]]) -> bool:
        """
        Default stopping criterion that never stops the conversation.

        Parameters
        ----------
        tested_client_history : List[Dict[str, str]]
            The history of the tested client.

        Returns
        -------
        bool
            Always returns False.
        """
        return False

    @staticmethod
    def default_tested_client_response_handler(tested_client_response: str, **kwargs) -> str:
        """
        Default tested_client_response_handler function that returns the response unchanged.

        Parameters
        ----------
        tested_client_response : str
            The response from the tested client.
        **kwargs : dict
            Additional keyword arguments (not used).

        Returns
        -------
        str
            The original tested client's response.

        # Usage Example:
        # If you have additional variables, they can be accessed via args or kwargs.
        # For example, to append a suffix from kwargs:
        # suffix = kwargs.get('suffix', '')
        # return tested_client_response + suffix
        """
        return tested_client_response

    def start_conversation(self, start_prompt: str) -> Optional[bool]:
        """
        Starts the conversation with the attacker and alternates between attacker and tested client.

        Parameters
        ----------
        start_prompt : str
            The initial prompt sent by the attacker to start the conversation.

        Returns
        -------
        Optional[bool]
            Returns True if the stopping criterion was met, otherwise False. In case of exception returns None.
        """
        logger.debug("Starting multi-stage conversation.")

        # Attacker initiates the conversation
        attacker_response = self.attacker_session.say(start_prompt)
        if attacker_response is None:
            return None
        logger.debug(f"Step {self.current_step}: Attacker response: {attacker_response}")

        while True:
            # Send attacker's response to the tested client and receive tested client's response
            if self.attacker_response_separator:
                attacker_response = attacker_response.split(self.attacker_response_separator)[-1]
            tested_client_response = self.tested_client_session.say(attacker_response.strip())
            logger.debug(f"Step {self.current_step}: Tested client response: {tested_client_response}")

            # Check stopping criterion by history
            if self.stop_criterion(tested_client_history=self.tested_client_session.history):
                logger.debug("Stopping criterion met.")
                return True

            # Check history limit
            if self.current_step >= self.history_limit:
                logger.debug("History limit exceeded.")
                return False

            # Handling the tested client's response before passing it to the attacker
            # (e.g. adding scoring, more instructions for attacker)
            attacker_prompt = self.tested_client_response_handler(
                tested_client_response if tested_client_response else "Error", *self.refine_args, **self.refine_kwargs
            )
            logger.debug(f"Step {self.current_step}: Attacker prompt: {attacker_prompt}")

            # Send the handled tested client's response to the attacker for refinement and sending next iteration
            attacker_response = self.attacker_session.say(attacker_prompt)
            logger.debug(f"Step {self.current_step}: Attacker response: {attacker_response}")
            if attacker_response is None:
                return None

            # Increment step
            self.current_step += 1
            logger.debug(f"Current step incremented to: {self.current_step}")

    def get_attack_prompts(self) -> List[Dict[str, str]]:
        """
        Returns attacking prompts from the history of the system being tested.

        Returns
        -------
        List[Dict[str, str]]
            Attacking prompts.
        """
        return [message for message in self.tested_client_session.history if message["role"] == "user"]

    def get_tested_client_responses(self) -> List[Dict[str, str]]:
        """
        Returns the responses of the system under test.

        Returns
        -------
        List[Dict[str, str]]
            The responses of the tested client's session.
        """
        return [message for message in self.tested_client_session.history if message["role"] == "assistant"]
