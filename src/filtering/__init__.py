from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, List

from src.search import ExtractSchema
from src.tool.wraps import measure_time


@dataclass
class GroupedContent:
    summaries: Dict[str, List[str]]

    def __init__(self):
        self.summaries = defaultdict(list)

    def add_summary(self, summary: ExtractSchema) -> None:
        self.summaries[summary.category.value].append(summary.content)

    def get_category_content(self, category: str) -> List[str]:
        return self.summaries.get(category, [])

    def get_all_categories(self) -> List[str]:
        return list(self.summaries.keys())

    def limit_category(self, category: str, max_items: int) -> None:
        if category in self.summaries:
            self.summaries[category] = self.summaries[category][:max_items]

@measure_time
def apply_filter_to(content_summaries: list[ExtractSchema]) -> GroupedContent:
    grouped = GroupedContent()

    for summary in content_summaries:
        grouped.add_summary(summary)

    return grouped

    # TODO: Order using LLM by category, descendentemente por importancia en base a lo que la IA decida

    # if len(content_summaries['SCIENT']) > 2:
    #     grouped_summaries['SCIENT'] = [grouped_summaries['SCIENT'][0], grouped_summaries['SCIENT'][1]]
    #
    # if len(grouped_summaries['SPORTS']) > 2:
    #     grouped_summaries['SPORTS'] = [grouped_summaries['SPORTS'][0], grouped_summaries['SPORTS'][1]]
    #
    # if len(grouped_summaries['SPORTS']) > 1:
    #     grouped_summaries['WEATHER'] = [grouped_summaries['WEATHER'][0]]