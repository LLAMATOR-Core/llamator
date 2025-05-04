import logging
from pathlib import Path
from typing import Generator, List, Optional

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
        attack_prompts: List[str] = []
        responses: List[str] = []
        statuses: List[str] = []
        try:
            # TODO: add attack model for changing verb tenses in prompts (past and future)
            # based on custom or default harmful dataset with present form
            dataset_filename = Path(__file__).parent.parent / "attack_data" / "past_tense.parquet"
            data = pd.read_parquet(dataset_filename, engine="pyarrow")
            data = self._prepare_attack_dataset(dataset=data)

            for attack_prompt_index, row in data.iterrows():
                yield StatusUpdate(
                    self.client_config,
                    self.info["code_name"],
                    self.status,
                    "Attacking",
                    attack_prompt_index,
                    self.num_attempts,
                )
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
                        current_status = "Broken"
                        self.status.report_breach(attack_prompt, response)
                    else:
                        current_status = "Resilient"
                        self.status.report_resilient(attack_prompt, response)
                responses.append(response)
                statuses.append(current_status)

            # Save artifacts for report
            self._save_attack_artifacts(attack_prompts=attack_prompts, responses=responses, statuses=statuses)

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
