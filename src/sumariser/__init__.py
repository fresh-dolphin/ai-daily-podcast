import os

import httpx
from pydantic import ValidationError
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.search import ExtractSchema
from src.tool.wraps import measure_async_time


@retry(
    retry=retry_if_exception_type(httpx.HTTPStatusError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=60, max=120),
    reraise=True
)
async def make_api_request(content: str) -> httpx.Response:
    latitude_project_id = os.environ["LATITUDE_PROJECT_ID"]
    latitude_api_url = f"https://gateway.latitude.so/api/v3/projects/{latitude_project_id}/versions/live/documents/run"
    return httpx.post(
        url=latitude_api_url,
        headers={
            "Authorization": f"Bearer {os.environ['LATITUDE_AUTH_TOKEN']}",
            "Content-Type": "application/json"
        },
        json={
            "path": "news_filter",
            "stream": False,
            "parameters": {
                "story": content
            }
        },
        timeout=None
    )

def clean_json_response(text: str) -> str:
    if text.startswith('```json') and text.endswith('```'):
        return text.removeprefix('```json').removesuffix('```').strip().encode('utf-8').decode('utf-8')
    return text.strip().encode('utf-8').decode('utf-8')

@measure_async_time
async def generate_sumaries_from(contents: list[str]) -> list[ExtractSchema]:
    responses: list[ExtractSchema] = []
    for content in contents:
        try:
            http_response = await make_api_request(content)
            http_response.raise_for_status()

            response = clean_json_response(http_response.json()['response']['text'])

            responses.append(ExtractSchema.model_validate_json(response))
        except httpx.HTTPStatusError as exc:
            print(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        except ValidationError as exc:
            print(repr(exc.errors()))
        except Exception as e:
            print(f"Error while generating summary for:\n {content}...")
            print(e)
    return responses
