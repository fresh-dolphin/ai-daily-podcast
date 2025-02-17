import os
from datetime import datetime
from pathlib import Path

from langchain_community.chat_models import ChatLiteLLM


def generate_podcast_from(
    stories: dict[str, list],
    project_dir: Path
) -> str:
    model_provider = "openrouter"
    model_name = "google/gemini-2.0-pro-exp-02-05"
    model_tag = "free"

    print(f"Model in use: {model_provider}/{model_name}:{model_tag}")

    system_prompt: str
    with open(f"{project_dir}/prompts/{model_name}/podcast_script.txt") as f:
        system_prompt = f.read()

    today = datetime.today().strftime('%Y-%m-%d')

    prompt = [
        ("system", system_prompt),
        ("user", f"Hoy es {today} y las noticias que hemos encontrado hoy son {stories}")
    ]

    llm = ChatLiteLLM(
        model_name=f"{model_provider}/{model_name}:{model_tag}",
        openrouter_api_key=os.environ["OPENROUTER_API_KEY"],
        temperature=0.5
    )

    response = llm.invoke(prompt)
    return response.content