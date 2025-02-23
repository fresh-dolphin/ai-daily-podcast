import ast
import os
from datetime import datetime

import httpx


def generate_podcast_from(
    stories: dict[str, list],
) -> str:
    latitude_project_id = os.environ["LATITUDE_PROJECT_ID"]
    latitude_api_url = f"https://gateway.latitude.so/api/v3/projects/{latitude_project_id}/versions/live/documents/run"

    today = datetime.today().strftime('%Y-%m-%d')

    http_response = httpx.post(
        url=latitude_api_url,
        headers={
            "Authorization": f"Bearer {os.environ['LATITUDE_AUTH_TOKEN']}",
            "Content-Type": "application/json"
        },
        json={
            "path": "podcast_script",
            "stream": False,
            "parameters": {
                "today": today,
                "stories": stories
            }
        },
        timeout=None
    )

    try:
        http_response.raise_for_status()
        llm_response = ast.literal_eval(http_response.text)['response']['text']
        return llm_response
    except httpx.HTTPStatusError as exc:
        print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        raise exc