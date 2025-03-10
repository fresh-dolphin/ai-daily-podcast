import os
import re
from typing import Optional

from crawl4ai import BrowserConfig, LLMExtractionStrategy, AsyncWebCrawler, CrawlerRunConfig, CacheMode, \
    DefaultMarkdownGenerator, PruningContentFilter, LXMLWebScrapingStrategy

from src.search.model.extract_schema import ExtractSchema
from src.search.model.source import Source
from src.tool.wraps import measure_async_time


class Searcher:
    @measure_async_time
    async def get_news_from_sources(
            self,
            sources: list[Source],
            limit_news: Optional[int] = None
    ) -> list[str]:
        async with AsyncWebCrawler(config=self.__get_browser_config()) as crawler:
            links: list[str] = []
            for source in sources:
                crawled_links = await self.__get_news_link_from(crawler, source)
                print(f"[{source.url}] -> {len(crawled_links)} links crawled")

                if limit_news: crawled_links = crawled_links[:limit_news]
                links.extend(crawled_links)

            print(f"Start content crawling from {len(links)} links")
            return await self.__get_content_from(crawler, links)

    @staticmethod
    def __get_browser_config() -> BrowserConfig:
        return BrowserConfig(
            headless=True,
            user_agent_mode="random",
            text_mode=True,
        )

    async def __get_news_link_from(self, crawler: AsyncWebCrawler, source: Source) -> list[str]:
        result = await crawler.arun(
            url=source.url,
            config=CrawlerRunConfig(
                exclude_external_links=True,
                exclude_external_images=True,
                remove_overlay_elements=True,
                cache_mode=CacheMode.DISABLED,
                scraping_strategy=LXMLWebScrapingStrategy()
            )
        )

        if source.pattern_filter:
            filter_pattern = re.compile(source.pattern_filter)

            links = []
            for link in result.links['internal']:
                if filter_pattern.match(link['href']):
                    links.append(link['href'])
        else:
            links = [link['href'] for link in result.links['internal']]

        return links

    async def __get_content_from(self, crawler: AsyncWebCrawler, links: list[str]) -> list[str]:
        results = await crawler.arun_many(
            urls=links,
            config=CrawlerRunConfig(
                excluded_tags=["nav", "footer", "header"],
                markdown_generator=self.__get_md_generator(),
                cache_mode=CacheMode.DISABLED,
                scraping_strategy=LXMLWebScrapingStrategy()
            )
        )

        stories: list[str] = []
        for result in results:
            if result.success:
                stories.append(result.markdown.fit_markdown)
            else:
                print(f"Error in {result.url}:\n {result.error_message}")
        return stories

    @staticmethod
    def __get_llm_strategy(crawl_news_prompt: str) -> LLMExtractionStrategy:
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

    @staticmethod
    def __get_md_generator() -> DefaultMarkdownGenerator:
        prune_filter = PruningContentFilter(
            threshold=0.5,
            threshold_type="dynamic"
        )

        return DefaultMarkdownGenerator(
            content_filter=prune_filter,
            options={
                "ignore_links": True,
                "ignore_images": True,
                "escape_html": True,
                "body_width": 80,
                "skip_internal_links": True
            }
        )