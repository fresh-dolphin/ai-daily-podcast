from enum import Enum

from pydantic import BaseModel


class Category(Enum):
    GENERAL = "GENERAL"
    POLITIC = "POLITIC"
    CULTURE = "CULTURE"
    SCIENCE = "SCIENCE"
    SPORTS = "SPORTS"
    ECONOMY = "ECONOMY"
    ENTERTAINMENT = "ENTERTAINMENT"
    WEATHER = "WEATHER"

    @classmethod
    def from_str(cls, value: str) -> "Category":
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Invalid category: {value}")

    def __str__(self) -> str:
        return self.value

class ExtractSchema(BaseModel):
    content: str
    category: Category

    @classmethod
    def to_dict_list(cls, items: list["ExtractSchema"]) -> list[dict]:
        return [item.model_dump() for item in items]