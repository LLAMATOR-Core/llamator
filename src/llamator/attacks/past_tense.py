import logging
import os
from pathlib import Path
from typing import Generator, Optional

import pandas as pd

from ..attack_provider.attack_registry import register_test
from ..attack_provider.test_base import StatusUpdate, TestBase
from ..attack_provider.util import contains_refusal_keywords
from ..client.attack_config import AttackConfig
from ..client.chat_client import ChatSession
from ..client.client_config import ClientConfig

logger = logging.getLogger(__name__)


@register_test
class TestPastTense(TestBase):
    """Challenges the LLM with a dataset of harmful behavior prompts in past tense form."""

    test_name = "past_tense"
    info = {
        "name": "Past Tense Attack",
        "code_name": "past_tense",
        "description": {
            "en": "Challenges the LLM with a dataset of harmful behavior prompts in past tense form.",
            "ru": "Проверяет устойчивость модели к выполнению вредных запросов, сформулированных в прошедшем времени."
        },
        "github_link": "https://github.com/RomiconEZ/llamator/blob/release/src/llamator/attacks/past_tense.py"
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
        super().__init__(
            client_config,
            attack_config,
            artifacts_path=artifacts_path,
            num_attempts=num_attempts,
            *args,
            **kwargs,
        )

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
            logging.info(f"Past Tense attack report saved to {csv_path}")

    def run(self) -> Generator[StatusUpdate, None, None]:
        # Getting the path to the directory where the file is located past_tense.py
        current_dir = Path(__file__).parent
        dataset_filename = current_dir.parent / "attack_data" / "past_tense.parquet"

        logger.info(f"Dataset filename: {dataset_filename}")
        data = pd.read_parquet(dataset_filename, engine="fastparquet")
        rows_count = data.shape[0]

        if self.num_attempts <= rows_count:
            # If dataset is larger than requested number of samples, reduce dataset by taking num_attempts samples
            data = data.sample(n=self.num_attempts)
        else:
            # If dataset is smaller than requested number of attack samples, fit the dataset repeating until num_attempts is reached
            data = (
                pd.concat([data] * (self.num_attempts // len(data) + 1))[: self.num_attempts]
                .sort_index()
                .reset_index(drop=True)
            )

        # Lists to store prompts, responses, and statuses for report generation
        attack_prompts = []
        responses = []
        statuses = []

        # Generate list of attack prompt variations
        yield StatusUpdate(self.client_config, self.info['code_name'], self.status, "Attacking", 0, self.num_attempts)

        for attack_prompt_index, row in data.iterrows():
            attack_prompt = row["goal"]
            attack_prompts.append(attack_prompt)
            chat = ChatSession(
                self.client_config.get_target_client(),
                self.client_config.get_system_prompts(),
            )
            response = chat.say(attack_prompt)
            if not response:
                logger.warning("Error while attacking against target LLM (didn't receive response) ...")
                self.status.report_error(attack_prompt)
                current_status = "Error"
            else:
                # Verify the response to determine if this specific attack was successful
                verified = not contains_refusal_keywords(response)
                logger.info(f"Test '{self.info['name']}': attack prompt #{attack_prompt_index}: {attack_prompt}")
                logger.info(
                    f"Test '{self.info['name']}': attack response #{attack_prompt_index} break_success={verified}): {response}"
                )
                if verified:
                    self.status.report_breach(attack_prompt, response)
                    current_status = "Broken"
                else:
                    self.status.report_resilient(attack_prompt, response)
                    current_status = "Resilient"

            # Append data for report
            responses.append(response)
            statuses.append(current_status)

            yield StatusUpdate(
                self.client_config,
                self.info['code_name'],
                self.status,
                "Attacking",
                attack_prompt_index,
                self.num_attempts,
            )

        # Prepare data for report generation
        self._prepare_attack_data(attack_prompts, responses, statuses)

        yield StatusUpdate(
            self.client_config,
            self.info['code_name'],
            self.status,
            "Finished",
            self.num_attempts,
            self.num_attempts,
        )
