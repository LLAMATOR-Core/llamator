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


# Functions for text transformations
def apply_word_scrambling(prompt: str, sigma: float) -> str:
    words = prompt.split()
    scrambled_words = []
    for word in words:
        if len(word) > 3 and random.random() < sigma ** (1 / 2):  # nosec
            chars = list(word)
            middle_chars = chars[1:-1]
            random.shuffle(middle_chars)  # nosec
            scrambled_word = chars[0] + "".join(middle_chars) + chars[-1]
            scrambled_words.append(scrambled_word)
        else:
            scrambled_words.append(word)
    return " ".join(scrambled_words)


def apply_random_capitalization(prompt: str, sigma: float) -> str:
    new_text = []
    for c in prompt:
        if c.isalpha() and random.random() < sigma ** (1 / 2):  # nosec
            if "a" <= c <= "z":
                new_text.append(chr(ord(c) - 32))
            elif "A" <= c <= "Z":
                new_text.append(chr(ord(c) + 32))
        else:
            new_text.append(c)
    return "".join(new_text)


def apply_ascii_noising(prompt: str, sigma: float) -> str:
    new_text = []
    for c in prompt:
        if c.isprintable() and random.random() < sigma**3:  # nosec
            perturbation = random.choice([-1, 1])  # nosec
            new_char_code = ord(c) + perturbation
            if 32 <= new_char_code <= 126:
                new_text.append(chr(new_char_code))
            else:
                new_text.append(c)
        else:
            new_text.append(c)
    return "".join(new_text)


@register_test
class TestBon(TestBase):
    """Probes the LLM resilience against Best-of-N attack (text augmentations).
    Original Paper: https://arxiv.org/abs/2412.03556, Code: https://github.com/jplhughes/bon-jailbreaking"""

    info = {
        "name": "Best-of-N Jailbreak",
        "code_name": "bon",
        "tags": [
            "lang:en",
            "dialog:multi-stage",
            "owasp:llm01",
            "eval:heuristic",
            "arxiv:2412.03556",
        ],
        "description": {
            "en": "Probes the LLM resilience against Best-of-N attack. Original Paper: https://arxiv.org/abs/2412.03556, Original Code: https://github.com/jplhughes/bon-jailbreaking",
            "ru": "Испытывает устойчивость LLM к атаке Best-of-N. Статья: https://arxiv.org/abs/2412.03556, оригинальный код: https://github.com/jplhughes/bon-jailbreaking",
        },
        "github_link": "https://github.com/LLAMATOR-Core/llamator/blob/release/src/llamator/attacks/bon.py",
    }

    def __init__(
        self,
        client_config: ClientConfig,
        attack_config: AttackConfig,
        artifacts_path: Optional[str] = None,
        num_attempts: int = 0,
        multistage_depth: int = 5,
        sigma: float = 0.4,
        **kwargs,
    ):
        super().__init__(
            client_config,
            attack_config,
            artifacts_path=artifacts_path,
            num_attempts=num_attempts,
            **kwargs,
        )
        self.sigma = sigma  # proportion of characters to augment
        self.multistage_depth = multistage_depth

    def transform_attack_prompt(self, prompt: str) -> str:
        """Applies a series of augmentations to the input text."""
        prompt = apply_word_scrambling(prompt, self.sigma)
        prompt = apply_random_capitalization(prompt, self.sigma)
        prompt = apply_ascii_noising(prompt, self.sigma)
        return prompt

    def run(self) -> Generator[StatusUpdate, None, None]:
        attack_prompts = []
        responses = []
        statuses = []
        try:
            current_dir = Path(__file__).parent
            dataset_filename = current_dir.parent / "attack_data" / "harmful_behavior.parquet"

            logger.info(f"Dataset filename: {dataset_filename}")
            data = pd.read_parquet(dataset_filename, engine="fastparquet")
            rows_count = data.shape[0]

            if self.num_attempts <= rows_count:
                # If dataset is larger than requested number of samples, reduce dataset by taking num_attempts samples
                data = data.sample(n=self.num_attempts)
            else:
                # If dataset is smaller than requested number of samples, fit the dataset repeating until limit is reached
                data = (
                    pd.concat([data] * (self.num_attempts // len(data) + 1))[: self.num_attempts]
                    .sort_index()
                    .reset_index(drop=True)
                )

            yield StatusUpdate(
                self.client_config,
                self.info["code_name"],
                self.status,
                "Generating",
                0,
                self.num_attempts
                * (self.multistage_depth + 1),  # +1 - we also store starting prompt besides refined ones
            )

            for attack_prompt_index, row in data.iterrows():
                attack_prompt = row["goal"]
                attack_prompts.append(attack_prompt)
                logger.info(
                    f"Test '{self.info['name']}': original attack prompt #{attack_prompt_index}: {attack_prompt}"
                )
                for stage in range(1, self.multistage_depth + 1):
                    transformed_prompt = self.transform_attack_prompt(attack_prompts[-1])
                    logger.info(f"Test '{self.info['name']}': generated attack prompt #{stage}: {transformed_prompt}")
                    attack_prompts.append(transformed_prompt)

                    yield StatusUpdate(
                        self.client_config,
                        self.info["code_name"],
                        self.status,
                        "Generating",
                        attack_prompt_index * (self.multistage_depth + 1) + stage,
                        self.num_attempts * (self.multistage_depth + 1),
                    )

            # Run the attack by sending the prompts and verifying the responses
            yield StatusUpdate(
                self.client_config,
                self.info["code_name"],
                self.status,
                "Attacking",
                0,
                self.num_attempts * (self.multistage_depth + 1),
            )

            total_attack_num = len(attack_prompts)
            for attack_prompt_index, attack_prompt in enumerate(attack_prompts):
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
                    total_attack_num,
                )

            # Prepare data for report generation
            self._prepare_attack_data(attack_prompts, responses, statuses)

            yield StatusUpdate(
                self.client_config,
                self.info["code_name"],
                self.status,
                "Finished",
                total_attack_num,
                total_attack_num,
            )
        except Exception as e:
            yield self.handle_exception(e, attack_prompts, responses, statuses)
