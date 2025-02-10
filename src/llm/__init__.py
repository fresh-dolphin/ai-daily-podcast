import os
from datetime import datetime
from pathlib import Path

from langchain_community.chat_models import ChatLiteLLM

def generate_podcast_from(
    stories: list[str],
    project_dir: Path
) -> str:
    with open(f"{project_dir}/prompts/google/gemini-2.0-pro/podcast_script.txt") as f:
        system_prompt = f.read()

    today = datetime.today().strftime('%Y-%m-%d')

    prompt = [
        ("system", system_prompt),
        ("user", f"Hoy es {today} y las noticias que hemos encontrado hoy son {stories}")
    ]

    llm = ChatLiteLLM(
        model_name="openrouter/google/gemini-2.0-pro-exp-02-05:free",
        openrouter_api_key=os.environ["OPENROUTER_API_KEY"],
        temperature=0.5
    )

    print(f"Model in use {llm.model_name}")

    result = llm.invoke(prompt)
    print(f"LLM usage {result.usage_metadata}")

    return result.content