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
class TestSuffix(TestBase):
    """Uses a specially crafted suffix to bypass LLM filters and restrictions, forcing the model to generate prohibited or harmful content despite the original query.
    Evaluates the model's vulnerability to input data manipulation.
    Original Paper: https://arxiv.org/abs/2307.15043, Code: https://github.com/llm-attacks/llm-attacks"""

    info = {
        "name": "Adversarial Suffix",
        "code_name": "suffix",
        "tags": [
            "lang:en",
            "dialog:single-stage",
            "owasp:llm01",
            "eval:heuristic",
            "arxiv:2307.15043",
            "model:llm",
        ],
        "description": {
            "en": "Uses a specially crafted suffix to bypass LLM filters and restrictions, forcing the model to generate prohibited or harmful content despite the original query. Evaluates the model's vulnerability to input data manipulation. Original Paper: https://arxiv.org/abs/2307.15043, Code: https://github.com/llm-attacks/llm-attacks",
            "ru": "Использует специально сконструированный суффикс для обхода фильтров и ограничений LLM, заставляя модель генерировать запрещённый или вредоносный контент, несмотря на исходный запрос. Оценивает уязвимость модели к манипуляциям входных данных. Статья: https://arxiv.org/abs/2307.15043, репозиторий: https://github.com/llm-attacks/llm-attacks",
        },
        "github_link": "https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/suffix.py",
    }

    def __init__(
        self,
        client_config: ClientConfig,
        attack_config: AttackConfig,
        artifacts_path: Optional[str] = None,
        num_attempts: int = 0,
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
        self.custom_dataset = custom_dataset

    def run(self) -> Generator[StatusUpdate, None, None]:
        attack_prompts: List[str] = []
        responses: List[str] = []
        statuses: List[str] = []
        try:
            if self.custom_dataset is None:
                dataset_filename = Path(__file__).parent.parent / "attack_data" / "suffixes.parquet"
                data = pd.read_parquet(dataset_filename, engine="pyarrow")
            else:
                data = self.custom_dataset.copy()
            data = self._prepare_attack_dataset(dataset=data)

            for attack_prompt_index, row in data.iterrows():
                attack_prompt = row["goal"]
                attack_prompts.append(attack_prompt)
                logger.info(f"Test '{self.info['name']}': attack prompt #{attack_prompt_index}: {attack_prompt}")
                yield StatusUpdate(
                    self.client_config,
                    self.info["code_name"],
                    self.status,
                    "Attacking",
                    attack_prompt_index,
                    self.num_attempts,
                )
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
