import logging
import os
import shutil
from pathlib import Path
from typing import List

from datasets import load_dataset
from git import Repo

logger = logging.getLogger(__name__)


class MAttackDataPreparator:
    def __init__(
        self, base_path: str = "attack_data/vlm_m_attack", dataset: str = "bigscale_100", target_subfolder: str = "1"
    ):
        self.base_path = Path(base_path)
        self.dataset = dataset
        self.dataset_path = self.base_path / dataset
        self.target_subfolder = target_subfolder

        self.github_repo = "https://github.com/VILA-Lab/M-Attack.git"
        self.clone_path = Path(base_path) / "test_repo"

    def prepare(self, variations=["4", "8", "16"], limit: int = -1):
        if os.path.exists(self.dataset_path):
            logger.warning("Images already downloaded.")
            return
        self._download_images(variations, limit)
        try:
            self._download_from_github()
        except Exception as e:
            logger.warning(f"GitHub repo unavailable: {e}")

    def _download_images(self, variations: List[str], limit: int):
        logger.info("Downloading images from Hugging Face...")
        dataset = load_dataset("MBZUAI-LLM/M-Attack_AdvSamples", split="train")
        os.makedirs(self.dataset_path, exist_ok=True)

        variation_set = set(variations)
        counter = 0

        for item in dataset:
            epsilon = str(item["epsilon"])
            image_path = str(os.path.join(*(item["image"].filename).split(os.sep)[-2:]))

            if epsilon not in variation_set:
                continue

            image = item["image"]
            variation_dir = self.dataset_path / epsilon
            variation_dir.mkdir(parents=True, exist_ok=True)

            save_path = self.dataset_path / f"{image_path}"
            image.save(save_path)
            counter += 1

            if 0 < limit <= counter:
                break

        logger.info(f"Saved {counter} images.")

    def _download_from_github(self):
        logger.info("Attempting to download target files from GitHub...")
        if not self.clone_path.exists():
            Repo.clone_from(self.github_repo, str(self.clone_path))

        target_src = self.clone_path / "resources" / "images" / "target_images" / self.target_subfolder
        target_dst = self.base_path / "target" / self.dataset
        target_dst.mkdir(parents=True, exist_ok=True)

        for file_name in ["keywords.json", "caption.json"]:
            shutil.copyfile(target_src / file_name, target_dst / file_name)
            logger.info(f"Copied {file_name}")

        shutil.copyfile(self.clone_path / "README.md", self.base_path / "README.md")
        shutil.rmtree(self.clone_path)
        logger.info("GitHub clone cleaned up.")
