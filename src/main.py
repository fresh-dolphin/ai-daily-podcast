import asyncio
import os
import time
from pathlib import Path

from dotenv import load_dotenv

from src import llm
from src.crawler import Crawler
from src.filtering import apply_filter_to
from src.tool import save_dict_to_file, save_text_to_file, get_output_dir


async def retrieve_news_links(crawler: Crawler, news_source: list[str]):
    links: list[str] = []
    for source in news_source:
        crawled_links = await crawler.get_news_link_from(source)
        print(f"{len(crawled_links)} links crawled from {source}")
        links.extend(crawled_links)
    return links

async def main():
    start_time = time.time()

    load_dotenv()

    project_root_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
    output_dir = get_output_dir(project_root_dir)

    news_source = [
        "https://www.rtve.es/noticias/ultimas-noticias/",
    ]

    print("STEP 1: Retrieving news from following sources:", news_source)
    crawler = Crawler(project_root_dir)

    links = await retrieve_news_links(crawler, news_source)

    content_summaries = await crawler.get_summaries_from(links)
    print(f"Processed {len(content_summaries)} of {len(links)} links")

    content_summaries_dict = [content.model_dump() for content in content_summaries]
    save_dict_to_file(content_summaries_dict, f"{output_dir}/content_summaries.json")

    print("STEP 2: Apply filters to crawled content...")
    content_summaries_grouped = apply_filter_to(content_summaries)

    save_dict_to_file(content_summaries_grouped, f"{output_dir}/content_summaries_grouped.json")

    print("STEP 3: Generating podcast script from news...")
    podcast_script = llm.generate_podcast_from(content_summaries_grouped, project_dir=project_root_dir)
    save_text_to_file(podcast_script, f"{output_dir}/podcast_script.txt")

    print("STEP 4: Generating audio...")
    # voice.generate_audio_from(podcast_script, output_dir)

    print("~~~ It's done! Have a good day ~~~")
    print(f"Execution time: {time.time() - start_time} seconds")

if __name__ == "__main__":
    asyncio.run(main())
