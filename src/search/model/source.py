from typing import Optional


class Source:
    def __init__(self, url: str, pattern_filter: Optional[str] = None):
        self.url = url
        self.pattern_filter = pattern_filter