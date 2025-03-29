import logging
import os
from abc import ABC, abstractmethod
from typing import Generator, List, Optional

import pandas as pd

from ..client.attack_config import AttackConfig
from ..client.client_config import ClientConfig


class TestLogEntry:
    """A single test step log entry"""

    def __init__(self, prompt: str, response: str, success: bool, additional_info: str):
        self.prompt = prompt  # The prompt sent to the LLM model
        self.response = response  # The response from the LLM model
        self.success = success  # True if the attack was successful (this means system prompt was weak), False otherwise
        self.additional_info = additional_info

    def __str__(self):
        return f"TestLog(prompt={self.prompt}, response={self.response}, success={self.success}, additional_info='{self.additional_info})'"


class TestStatus:
    """
    Keeps track of the successful and failed prompts, as well as the log of all interactions with the target LLM model.
    """

    def __init__(self):
        self.breach_count: int = 0
        self.resilient_count: int = 0
        self.error_count: int = 0
        self.total_count: int = 0
        self.finished: bool = False  # This test is finished and the results are final
        self.log: List[TestLogEntry] = []

    def __str__(self):
        return f"TestStatus(breach_count={self.breach_count}, resilient_count={self.resilient_count}, total_count={self.total_count}, log:{len(self.log)} entries)"

    def report_breach(
        self,
        prompt: str,
        response: str,
        additional_info: str = "Attack succesfully broke system prompt protection",
    ):
        """Reports a succesful breach of the system prompt"""
        self.breach_count += 1
        self.total_count += 1
        self.log.append(TestLogEntry(prompt, response, True, additional_info))

    def report_resilient(
        self,
        prompt: str,
        response: str,
        additional_info: str = "Attack failed to break system prompt protection",
    ):
        """Reports a failed attack, meaning the system prompt was resilient"""
        self.resilient_count += 1
        self.total_count += 1
        self.log.append(TestLogEntry(prompt, response, False, additional_info))

    def report_error(self, prompt: str, additional_info: str = "Error"):
        "Reports an error during the test"
        self.error_count += 1
        self.total_count += 1
        self.log.append(TestLogEntry(prompt, None, False, additional_info))


class StatusUpdate:
    """Represents a status update during the execution of a test"""

    def __init__(
        self,
        client_config: ClientConfig,
        test_name: str,
        status: TestStatus,
        action: str,
        progress_position: int,
        progress_total: int,
    ):
        self.test_name = test_name
        self.client_config: ClientConfig = client_config
        self.status: TestStatus = status
        self.action: str = action
        self.progress_position: int = progress_position
        self.progress_total: int = progress_total


class TestBase(ABC):
    """
    A base class for test classes. Each test represents a different kind of attack against the target LLM model.
    The test sends a sequence of prompts and evaluate the responses while updating the status.
    """

    info = {
        "name": "Test Name",
        "code_name": "test_name",
        "tags": [],
        "description": {
            "en": "Description in english",
            "ru": "Описание на русском",
        },
        "github_link": "",
    }

    def __init__(
        self,
        client_config: ClientConfig,
        attack_config: AttackConfig,
        artifacts_path: Optional[str] = None,
        num_attempts: int = 0,
        *args,
        **kwargs,
    ):
        self.test_description = self.__doc__
        self.client_config = client_config
        self.attack_config = attack_config
        self.status = TestStatus()
        self.artifacts_path = artifacts_path
        self.num_attempts = num_attempts

    @abstractmethod
    def run(self) -> Generator[StatusUpdate, None, None]:
        """
        An abstract method to be implemented by subclasses to run the test.
        This method is iterable. It yields StatusUpdate objects to report progress.
        """
        pass

    def _prepare_attack_data(self, attack_prompts: list[str], responses: list[str], statuses: list[str]) -> None:
        """
        Prepares attack data in a structured DataFrame format and saves it as a CSV file.

        Args:
            attack_prompts (list[str]): List of attack texts generated during the test.
            responses (list[str]): List of responses from the target system.
            statuses (list[str]): List of statuses ('broken', 'resilient', 'error') corresponding to each attack.

        Returns:
            None
        """
        # Create a DataFrame from the lists
        df = pd.DataFrame({"attack_text": attack_prompts, "response_text": responses, "status": statuses})

        # Save the DataFrame as a CSV file to the artifacts path
        if self.artifacts_path:
            csv_path = os.path.join(self.artifacts_path, f"{self.info['code_name']}.csv")
            df.to_csv(csv_path, index=False)
            logging.info(f"{self.info['name']} attack report saved to {csv_path}")

    def handle_exception(
        self, e: Exception, attack_prompts: list[str], responses: list[str], statuses: list[str]
    ) -> StatusUpdate:
        """
        Обрабатывает исключение, регистрируя оставшиеся попытки как ошибки, записывает информацию об ошибке,
        подготавливает данные для отчета и возвращает финальный статус теста.

        Parameters
        ----------
        e : Exception
            Исключение, которое произошло.
        attack_prompts : list[str]
            Список сгенерированных атак.
        responses : list[str]
            Список ответов на атаки.
        statuses : list[str]
            Список статусов для каждой атаки.

        Returns
        -------
        StatusUpdate
            Финальное обновление статуса с информацией о завершении теста.
        """
        logging.exception(f"Exception occurred during test {self.info['name']} execution")
        self.status.report_error(str(e), additional_info=f"Exception during test {self.info['name']} execution")
        self._prepare_attack_data(attack_prompts, responses, statuses)
        return StatusUpdate(
            self.client_config,
            self.info["code_name"],
            self.status,
            "Finished",
            self.num_attempts,
            self.num_attempts,
        )
