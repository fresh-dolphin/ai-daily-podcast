import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from src import llm, voice
from src.crawler.crawler import Crawler

ROOT_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent

def save_dict_to_file(dictionary, file_path):
    if os.path.exists(file_path):
        print(f"file {file_path} exists from previous execution, overriding...")
    with open(file_path, 'w+') as f:
        json.dump(dictionary, f, indent=2, ensure_ascii=False)

def save_text_to_file(text, file_path):
    if os.path.exists(file_path):
        print(f"file {file_path} exists from previous execution, overriding...")
    with open(file_path, 'w+') as f:
        f.write(text)

async def main():
    load_dotenv()

    news_source = [
        "https://www.rtve.es/noticias/ultimas-noticias/"
    ]

    today = datetime.today().strftime('%Y-%m-%d')

    out_dir = Path(f"{ROOT_DIR}/out/{today}/")
    out_dir.mkdir(parents=True, exist_ok=True)

    print("STEP 1: Retrieving news from following sources:", news_source)

    crawler = Crawler(ROOT_DIR)

    stories: list[str] = []
    for source in news_source:
        links = await crawler.get_news_link_from(source)
        print(f"Number of news items found: {len(links)}")

        summaries = await crawler.get_summaries_from(links)
        print(f"Processed {len(summaries)} of {len(links)}")

        stories.extend(summaries)

    save_dict_to_file(stories, f"{out_dir}/news.json")

    with open(f"{ROOT_DIR}/out/news.json") as f:
        stories = json.loads(f.read())

    print("STEP 2: Generating podcast script from news...")
    podcast = llm.generate_podcast_from(stories=stories, project_dir=ROOT_DIR)

    save_text_to_file(podcast, f"{out_dir}/podcast.txt")

    with open(f"{ROOT_DIR}/out/podcast-2025-02-08.txt") as f:
        podcast = f.read()

    print("STEP 3: Generating audio...")
    voice.generate_audio_from(podcast, ROOT_DIR)

    print("It's done! Have a good day")

if __name__ == "__main__":
    asyncio.run(main())
