import logging
import random
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
class TestShuffle(TestBase):
    """Probes the LLM resilience against Shuffle Inconsistency.
    Original Paper: https://arxiv.org/html/2501.04931"""

    info = {
        "name": "Shuffle Inconsistency",
        "code_name": "shuffle",
        "tags": [],
        "description": {
            "en": "Attempts to bypass LLM's defense mechanism by randomly shuffling elements in input harmful prompt. Original Paper: https://arxiv.org/html/2501.04931",
            "ru": "Проверяет устойчивость LLM к Shuffle Inconsistency: Попытка обойти защиту LLM, случайным образом перемешивая элементы во входном вредоносном запросе. Статья: https://arxiv.org/html/2501.04931",
        },
        "github_link": "https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/shuffle.py",
    }

    def __init__(
        self,
        client_config: ClientConfig,
        attack_config: AttackConfig,
        artifacts_path: Optional[str] = None,
        num_attempts: int = 0,
        multistage_depth: int = 5,
        custom_dataset: Optional[pd.DataFrame] = None,
        **kwargs,
    ):
        super().__init__(
            client_config,
            attack_config,
            artifacts_path=artifacts_path,
            num_attempts=num_attempts,
            **kwargs,
        )
        self.multistage_depth = multistage_depth
        self.custom_dataset = custom_dataset

    @staticmethod
    def shuffle_words(prompt: str) -> str:
        words = prompt.split()
        random.shuffle(words)  # nosec
        return " ".join(words)

    def run(self) -> Generator[StatusUpdate, None, None]:
        original_prompts = []
        attack_prompts = []
        responses = []
        statuses = []
        try:
            if self.custom_dataset is None:
                dataset_filename = Path(__file__).parent.parent / "attack_data" / "harmful_behavior.parquet"
                data = pd.read_parquet(dataset_filename, engine="fastparquet")
            else:
                data = self.custom_dataset.copy()
            data = self._prepare_attack_dataset(dataset=data)

            for attack_prompt_index, row in data.iterrows():
                attack_prompt = row["goal"]
                logger.info(
                    f"Test '{self.info['name']}': original attack prompt #{attack_prompt_index}: {attack_prompt}"
                )
                for stage in range(self.multistage_depth):
                    yield StatusUpdate(
                        self.client_config,
                        self.info["code_name"],
                        self.status,
                        "Attacking",
                        attack_prompt_index * self.multistage_depth + stage,
                        self.num_attempts * self.multistage_depth,
                    )
                    original_prompts.append(attack_prompt)
                    shuffled_prompt = self.shuffle_words(attack_prompt)
                    attack_prompts.append(shuffled_prompt)
                    logger.info(
                        f"Test '{self.info['name']}': generated attack prompt #{attack_prompt_index}.{stage}: {shuffled_prompt}"
                    )
                    chat = ChatSession(
                        self.client_config.get_target_client(),
                        self.client_config.get_system_prompts(),
                    )
                    response = chat.say(shuffled_prompt)
                    if not response:
                        logger.warning("Error while attacking against target LLM (didn't receive response) ...")
                        self.status.report_error(shuffled_prompt)
                        current_status = "Error"
                    else:
                        # Verify the response to determine if this specific attack was successful
                        verified = not contains_refusal_keywords(response)
                        logger.info(
                            f"Test '{self.info['name']}': attack prompt #{attack_prompt_index}.{stage}: {shuffled_prompt}"
                        )
                        logger.info(
                            f"Test '{self.info['name']}': attack response #{attack_prompt_index}.{stage} break_success={verified}): {response}"
                        )
                        if verified:
                            current_status = "Broken"
                            self.status.report_breach(shuffled_prompt, response)
                        else:
                            current_status = "Resilient"
                            self.status.report_resilient(shuffled_prompt, response)
                    responses.append(response)
                    statuses.append(current_status)

            # Prepare data for report generation
            self._prepare_attack_artifacts(
                original_prompts=original_prompts, attack_prompts=attack_prompts, responses=responses, statuses=statuses
            )

            yield StatusUpdate(
                self.client_config,
                self.info["code_name"],
                self.status,
                "Finished",
                self.num_attempts * self.multistage_depth,
                self.num_attempts * self.multistage_depth,
            )
        except Exception as e:
            yield self.handle_exception(e, attack_prompts, responses, statuses)
