import asyncio
import os

import httpx
from colorama import Fore
from pydantic import ValidationError

from src.search import ExtractSchema
from src.tool.pydantic import print_validation_error
from src.tool.wraps import measure_async_time


async def make_api_request(content: str) -> httpx.Response:
    latitude_project_id = os.environ["LATITUDE_PROJECT_ID"]
    latitude_api_url = f"https://gateway.latitude.so/api/v3/projects/{latitude_project_id}/versions/live/documents/run"

    async with httpx.AsyncClient() as client:
        response = await client.post(
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
        response.raise_for_status()
        return response

def clean_markdown_annotations(text: str) -> str:
    if text.startswith('```json') and text.endswith('```'):
        return text.removeprefix('```json').removesuffix('```').strip().encode('utf-8').decode('utf-8')
    return text

async def process_content(content: str):
    try:
        http_response = await make_api_request(content)
        llm_response = http_response.json()['response']['text']
        llm_cleaned_response = clean_markdown_annotations(llm_response)
        return content, ExtractSchema.model_validate_json(llm_cleaned_response), None
    except httpx.HTTPStatusError as exc:
        print(Fore.RED + f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
        return content, None, "http_error"
    except ValidationError as exc:
        print_validation_error(exc)
        return content, None, "json_validation_error"
    except Exception as exc:
        print(Fore.RED + exc)
        return content, None, "unknown_error"

@measure_async_time
async def generate_sumaries_from(
        contents: list[str],
        max_retries: int = 3,
        batch_size: int = 5
) -> list[ExtractSchema]:
    results = []
    content_to_process = contents.copy()

    if not content_to_process: return results

    for attempt in range(max_retries):
        print(Fore.YELLOW + f"Attempts {attempt + 1}/{max_retries} to process {len(content_to_process)} news")
        failed_requests = []

        for i in range(0, len(content_to_process), batch_size):
            print(f"Processing batch {i + batch_size}/{len(content_to_process)}")
            batch = content_to_process[i:i + batch_size]
            batch_results = await asyncio.gather(
                *[process_content(content) for content in batch],
                return_exceptions=False
            )

            for content, result, error_type in batch_results:
                if result is not None:
                    results.append(result)
                elif error_type == "http_error":
                    failed_requests.append(content)

        content_to_process = failed_requests

        if failed_requests and attempt < max_retries - 1:
            wait_time = 60
            print(f"{Fore.YELLOW}Waiting {wait_time}s before re-try {len(failed_requests)} no parsed news{Fore.RESET}")
            await asyncio.sleep(wait_time)
        else:
            break

    if content_to_process:
        print(f"{Fore.RED}{len(content_to_process)} can't be processed after {max_retries} re-tries{Fore.RESET}")

    return results
