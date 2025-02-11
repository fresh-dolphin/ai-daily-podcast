import asyncio
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from src import llm, voice

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

    # crawler = Crawler(ROOT_DIR)
    #
    # grouped_summaries = {
    #     "GENERAL": [],
    #     "POLITIC": [],
    #     "CULTURE": [],
    #     "SCIENT": [],
    #     "SPORTS": [],
    #     "WEATHER": []
    # }
    #
    # for source in news_source:
    #     links = await crawler.get_news_link_from(source)
    #     print(f"Number of news items found: {len(links)}")
    #
    #     summaries = await crawler.get_summaries_from(links)
    #     print(f"Processed {len(summaries)} of {len(links)}")
    #
    #     for summary in summaries:
    #         category = summary.get('category')
    #         if category and category in grouped_summaries:
    #             grouped_summaries[category].append(summary['content'])
    #         elif not category:
    #             print("Summary without category found and ignored")
    #         else:
    #             print(f"Summary with unknown category: {category}")
    #
    # save_dict_to_file(grouped_summaries, f"{out_dir}/news.json")

    # if len(grouped_summaries['SCIENT']) > 2:
    #     grouped_summaries['SCIENT'] = [grouped_summaries['SCIENT'][0], grouped_summaries['SCIENT'][1]]
    #
    # if len(grouped_summaries['SPORTS']) > 2:
    #     grouped_summaries['SPORTS'] = [grouped_summaries['SPORTS'][0], grouped_summaries['SPORTS'][1]]
    #
    # if len(grouped_summaries['SPORTS']) > 1:
    #     grouped_summaries['WEATHER'] = [grouped_summaries['WEATHER'][0]]
    #
    # save_dict_to_file(grouped_summaries, f"{out_dir}/curated_news.json")

    with open(f"{out_dir}/curated_news.json") as f:
        grouped_summaries = json.loads(f.read())

    print("STEP 2: Generating podcast script from news...")
    podcast = llm.generate_podcast_from(stories=grouped_summaries, project_dir=ROOT_DIR)

    save_text_to_file(podcast, f"{out_dir}/podcast.txt")

    print("STEP 3: Generating audio...")
    voice.generate_audio_from(podcast, out_dir)

    print("It's done! Have a good day")

def guard_at_least_one_source(sources):
    if len(sources) == 0:
        raise RuntimeError("You need to pass at least one source")

if __name__ == "__main__":
    asyncio.run(main())
