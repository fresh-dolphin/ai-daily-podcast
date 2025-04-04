import ast
import os

import httpx
from colorama import Fore
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_fixed

from src.tool.date import get_today_spanish_format
from src.tool.wraps import measure_time


def before_sleep(retry_state):
    print(f"Retry no. {retry_state.attempt_number}"
          f"Waiting {retry_state.next_action.sleep} seg...")

@retry(
    retry=retry_if_exception_type(httpx.HTTPStatusError),
    stop=stop_after_attempt(3),
    wait=wait_fixed(62),
    before_sleep=before_sleep,
    reraise=True
)
@measure_time
def generate_podcast_from(
    stories: dict[str, list],
) -> str:
    latitude_project_id = os.environ["LATITUDE_PROJECT_ID"]
    latitude_api_url = f"https://gateway.latitude.so/api/v3/projects/{latitude_project_id}/versions/live/documents/run"

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
                "today": get_today_spanish_format(),
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