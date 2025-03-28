from .client_config import ClientConfig


class JudgeConfig:
    def __init__(self, judge_client: ClientConfig):
        self.judge_client = judge_client
