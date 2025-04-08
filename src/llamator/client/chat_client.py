import logging
from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Tuple

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
    def interact(self, history: List[Dict[str, str]], messages: List[Dict[str, str]]) -> Dict[str, str]:
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
    say(user_prompt: str, use_history: bool = True) -> str | None
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

    def say(self, user_prompt: str) -> str | None:
        """
        Sends a user message to the LLM, updates the conversation history based on the use_history flag,
        and returns the assistant's response.

        Parameters
        ----------
        user_prompt : str
            The user's message to be sent to the LLM.

        Returns
        -------
        str | None
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
    history_limit : int
        The maximum allowed history length for the attacker.
    history_evaluation : Callable[..., Tuple[bool, str]]
        A function that determines whether to stop the conversation
        based on the tested client's responses and returns prompt for attacker.
    refine_args : tuple
        Additional positional arguments for tested_client_response_handler.
    refine_kwargs : dict
        Additional keyword arguments for tested_client_response_handler.
    current_step : int
        The current step of the attacker.

    Methods
    -------
    start_conversation(start_prompt: str) -> bool | None
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
        history_limit: Optional[int] = 20,
        history_evaluation: Optional[Callable[[List[Dict[str, str]]], Tuple[bool, str]]] = None,
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
        history_limit : int, optional
            The maximum number of messages allowed in the attacker's history. (default is 20)
        history_evaluation : Callable[[List[Dict[str, str]]], Tuple[bool, str]]], optional
            A function that takes the tested client's history and returns stop request and message for attack model.
            If None, returns False and the last response of Tested model. (default is None)
        refine_args : tuple, optional
            Additional positional arguments for tested_client_response_handler. (default is None)
        refine_kwargs : dict, optional
            Additional keyword arguments for tested_client_response_handler. (default is None)
        """
        self.attacker_session = attacker_session
        self.tested_client_session = tested_client_session
        self.history_limit = history_limit
        self.history_evaluation = (
            history_evaluation if history_evaluation is not None else self.default_history_evaluation
        )
        self.refine_args = refine_args if refine_args is not None else ()
        self.refine_kwargs = refine_kwargs if refine_kwargs is not None else {}
        self.current_step = 1

    @staticmethod
    def default_history_evaluation(tested_client_history: List[Dict[str, str]], *args, **kwargs) -> Tuple[bool, str]:
        """
        Default history evaluation that never stops the conversation.

        Parameters
        ----------
        tested_client_history : List[Dict[str, str]]
            The history of the tested client.

        Returns
        -------
        Tuple[bool, str]
            Always returns False and the last response of Tested client.
        """
        last_response = tested_client_history[-1]["content"] if tested_client_history else ""
        return False, last_response

    def start_conversation(self, start_prompt: str) -> bool | None:
        """
        Starts the conversation with the attacker and alternates between attacker and tested client.

        Parameters
        ----------
        start_prompt : str
            The initial prompt sent by the attacker to start the conversation.

        Returns
        -------
        bool | None
            Returns True if the stopping criterion was met, otherwise False. In case of exception returns None.
        """
        logger.debug("Starting multi-stage conversation.")

        # Attacker initiates the conversation
        attacker_response = self.attacker_session.say(start_prompt)
        if not attacker_response:
            return None
        logger.debug(f"Step {self.current_step}: Attacker response: {attacker_response}")

        while True:
            # Send attacker's response to the tested client and receive tested client's response
            tested_client_response = self.tested_client_session.say(attacker_response)
            logger.debug(f"Step {self.current_step}: Tested client response: {tested_client_response}")
            if not tested_client_response:
                return None

            # Evaluate client history (e.g. adding scoring, more instructions for attacker)
            is_broken, attacker_prompt = self.history_evaluation(
                tested_client_history=self.tested_client_session.history, *self.refine_args, **self.refine_kwargs
            )
            if is_broken:
                logger.debug("Stopping criterion met.")
                return True

            # Check history limit
            if self.current_step >= self.history_limit:
                logger.debug("History limit exceeded.")
                return False

            # Send the prompt to attacker for refinement and sending next iteration
            logger.debug(f"Step {self.current_step}: Attacker prompt: {attacker_prompt}")
            if not attacker_prompt:
                return None
            attacker_response = self.attacker_session.say(attacker_prompt)
            logger.debug(f"Step {self.current_step}: Attacker response: {attacker_response}")
            if not attacker_response:
                return None

            # Increment step
            self.current_step += 1
            logger.debug(f"Current step incremented to: {self.current_step}")

    def get_attacker_responses(self) -> List[Dict[str, str]]:
        """
        Retrieves the responses of the attacker.

        Returns
        -------
        List[Dict[str, str]]
            The responses of the attacker's session.
        """
        return [message for message in self.attacker_session.history if message["role"] == "assistant"]

    def get_tested_client_responses(self) -> List[Dict[str, str]]:
        """
        Retrieves the responses of the tested client.

        Returns
        -------
        List[Dict[str, str]]
            The responses of the tested client's session.
        """
        return [message for message in self.tested_client_session.history if message["role"] == "assistant"]
