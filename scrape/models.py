from dataclasses import dataclass
from typing import List


@dataclass
class Episode:
    tag: str
    link: str


@dataclass
class Anime:
    name: str
    episodes: List[Episode]
