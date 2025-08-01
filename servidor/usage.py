class DailyTokenCounter:
    def __init__(self):
        self.tokens_used = 0

    def add_tokens(self, tokens: int) -> None:
        self.tokens_used += tokens

    def get_tokens_used(self) -> int:
        return self.tokens_used

    def is_limit_exceeded(self, daily_limit: int) -> bool:
        return self.tokens_used >= daily_limit

    def reset(self) -> None:
        self.tokens_used = 0
