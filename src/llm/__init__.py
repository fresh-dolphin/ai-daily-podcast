import ast
import os
from datetime import datetime

import httpx
from colorama import Fore
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.tool.wraps import measure_time


def before_sleep(retry_state):
    print(f"Retry no. {retry_state.attempt_number}"
          f"Esperando {retry_state.next_action.sleep} segundos...")

@retry(
    retry=retry_if_exception_type(httpx.HTTPStatusError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=65, max=65),
    before_sleep=before_sleep,
    reraise=True
)
@measure_time
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
        print(Fore.RED + f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        raise exc