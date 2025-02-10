import json
import os
import re
from pathlib import Path

from crawl4ai import BrowserConfig, LLMExtractionStrategy, AsyncWebCrawler, CrawlerRunConfig, CacheMode, \
    DefaultMarkdownGenerator, PruningContentFilter

from src.crawler.extract_schema import ExtractSchema


class Crawler:
    def __init__(self, project_dir: Path):
        browser_config = BrowserConfig(
            headless=True,
            user_agent_mode="random",
            text_mode=True,
            light_mode=True
        )
        self.crawler = AsyncWebCrawler(config=browser_config)
        self.project_dir = project_dir

    async def get_news_link_from(self, source: str) -> list[str]:
        crawl_config = CrawlerRunConfig(
            exclude_external_links=True,
            exclude_social_media_links=True,
            remove_overlay_elements=True,
            cache_mode=CacheMode.DISABLED
        )

        async with self.crawler as crawler:
            result = await crawler.arun(url=source,config=crawl_config)

        filter_pattern = re.compile(r"^https://www.rtve.es/noticias/\d{8}/[a-zA-Z0-9\-]+/\d+\.shtml$")

        links = []
        for link in result.links['internal']:
            if filter_pattern.match(link['href']):
                links.append(link['href'])

        return links

    async def get_summaries_from(self, links: list[str]) -> list[dict]:
        with open(f"{self.project_dir}/prompts/nvidia/llama-3-1-nemotron-70b-instruct/crawler_instructions.txt") as f:
            crawl_news_prompt = f.read()

        llm_strategy = self.__get_llm_strategy(crawl_news_prompt)

        crawl_config = CrawlerRunConfig(
            extraction_strategy=llm_strategy,
            markdown_generator=self.__get_md_generator(),
            cache_mode=CacheMode.DISABLED
        )

        # dispatcher = MemoryAdaptiveDispatcher(
        #     memory_threshold_percent=70.0,
        #     check_interval=1.0,
        #     max_session_permit=10,
        #     monitor=CrawlerMonitor(
        #         display_mode=DisplayMode.DETAILED
        #     )
        # )

        stories: list = []

        async with self.crawler as crawler:
            results = await crawler.arun_many(
                urls=links,
                config=crawl_config,
            )

            llm_strategy.show_usage()

            for result in results:
                if result.success:
                    json_result = json.loads(result.extracted_content)[0]
                    if not json_result['error']:
                        stories.append(json.loads(result.extracted_content)[0])
                    else:
                        print(f"Error: {result.error_message}")
                else:
                    print(f"Error: {result.error_message}")

        return stories

    def __get_llm_strategy(self, crawl_news_prompt: str) -> LLMExtractionStrategy:
        return LLMExtractionStrategy(
            provider="openrouter/nvidia/llama-3.1-nemotron-70b-instruct:free",
            api_token=os.environ["OPENROUTER_API_KEY"],
            extraction_type="schema",
            schema=ExtractSchema.model_json_schema(),
            instruction=crawl_news_prompt,
            chunk_token_threshold=3500,
            overlap_rate=0.1,
            apply_chunking=True,
            input_format="fit_markdown",
            extra_args={"temperature": 1},
            verbose=True
        )

    def __get_md_generator(self) -> DefaultMarkdownGenerator:
        prune_filter = PruningContentFilter(
            threshold=0.5,
            threshold_type="dynamic",
            min_word_threshold=50
        )

        return DefaultMarkdownGenerator(
            content_filter=prune_filter,
            options={
                "ignore_links": True,
                "ignore_images": True,
                "escape_html": False,
                "body_width": 80
            }
        )