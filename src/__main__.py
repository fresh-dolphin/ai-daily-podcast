import asyncio
import os
from datetime import datetime
from pathlib import Path

from colorama import init, Fore
from dotenv import load_dotenv

from src import llm, voice
from src.filtering import apply_filter_to, GroupedContent
from src.search import Searcher, ExtractSchema
from src.search.model.source import Source
from src.sumariser import generate_sumaries_from
from src.tool import get_output_dir, save_dict_to_file, save_text_to_file
from src.tool.wraps import measure_async_time

init(autoreset=True)

load_dotenv()

@measure_async_time
async def main():
    project_root_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent
    output_dir = get_output_dir(project_root_dir)

    today = datetime.today().strftime('%Y-%m-%d')

    sources: list[Source] = [
        Source("https://rtve.es/noticias/ultimas-noticias/", r"^https:\/\/www\.rtve\.es\/noticias\/\d{8}\/[a-zA-Z0-9\-]+\/\d+\.shtml$"),
        Source("https://elpais.com/actualidad/", r"^https:\/\/elpais\.com\/[a-z-]+\/" + today + r"\/[a-z0-9-]+\.html$"), # r"^https:\/\/elpais\.com\/[a-z-]+\/\d{4}-\d{2}-\d{2}\/[a-z0-9-]+\.html$"
    ]

    print(Fore.CYAN + "[STEP 1] -> Searching news in the following sources:", [source.url for source in sources])
    content_news: list[str] = await Searcher().get_news_from_sources(sources, limit_news=None)

    print(Fore.CYAN + "[STEP 2] -> Apply summaries to crawled content...")
    content_news_summaries: list[ExtractSchema] = await generate_sumaries_from(content_news, batch_size=10)

    print(Fore.CYAN + "[STEP 3] -> Apply filters to crawled content...")
    content_summaries_grouped: GroupedContent = apply_filter_to(content_news_summaries)
    save_dict_to_file(content_summaries_grouped.summaries, f"{output_dir}/content_summaries_grouped.json")

    print(Fore.CYAN + "[STEP 4] -> Generating podcast script from news...")
    podcast_script = llm.generate_podcast_from(content_summaries_grouped.summaries)
    save_text_to_file(podcast_script, f"{output_dir}/podcast_script.txt")

    print(Fore.CYAN + "[STEP 5] -> Generating audio...")
    voice.generate_audio_from(podcast_script, output_dir)

    voice.add_audio_effects(
        audio_file=Path(f"{output_dir}/podcast_audio.mp3"),
        project_root_dir=project_root_dir,
        output_dir=output_dir
    )

    print("~~~ It's done! Have a good day ~~~")

if __name__ == "__main__":
    asyncio.run(main())