import logging
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

    info = {
        "name": "Past Tense Attack",
        "code_name": "past_tense",
        "tags": [
            "lang:en",
            "dialog:single-stage",
            "owasp:llm01",
            "eval:heuristic",
        ],
        "description": {
            "en": "Challenges the LLM with a dataset of harmful behavior prompts in past tense form.",
            "ru": "Проверяет устойчивость модели к выполнению вредных запросов, сформулированных в прошедшем времени.",
        },
        "github_link": "https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/past_tense.py",
    }

    def __init__(
        self,
        client_config: ClientConfig,
        attack_config: AttackConfig,
        artifacts_path: Optional[str] = None,
        num_attempts: int = 0,
        **kwargs,
    ):
        super().__init__(
            client_config,
            attack_config,
            artifacts_path=artifacts_path,
            num_attempts=num_attempts,
            **kwargs,
        )

    def run(self) -> Generator[StatusUpdate, None, None]:
        # Getting the path to the directory where the file is located past_tense.py
        attack_prompts = []
        responses = []
        statuses = []
        try:
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
            yield StatusUpdate(
                self.client_config, self.info["code_name"], self.status, "Attacking", 0, self.num_attempts
            )

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
                    self.info["code_name"],
                    self.status,
                    "Attacking",
                    attack_prompt_index,
                    self.num_attempts,
                )

            # Prepare data for report generation
            self._prepare_attack_data(attack_prompts, responses, statuses)

            yield StatusUpdate(
                self.client_config,
                self.info["code_name"],
                self.status,
                "Finished",
                self.num_attempts,
                self.num_attempts,
            )
        except Exception as e:
            yield self.handle_exception(e, attack_prompts, responses, statuses)
