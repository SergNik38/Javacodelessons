import asyncio
import aiohttp
import json
from typing import Dict, Any
from pathlib import Path


async def fetch_urls(
    input_file: str, output_file: str = "result.jsonl", max_concurrent: int = 5
) -> None:
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(input_file, "r") as f:
            urls = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return
    except Exception:
        return

    semaphore = asyncio.Semaphore(max_concurrent)
    results: Dict[str, Any] = {}

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False),
        timeout=aiohttp.ClientTimeout(total=300),
    ) as session:

        async def process_url(url: str) -> None:
            async with semaphore:
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            try:
                                data = []
                                async for chunk in response.content.iter_chunked(16384):
                                    data.append(chunk)
                                json_data = json.loads(b"".join(data))
                                results[url] = json_data
                            except json.JSONDecodeError:
                                results[url] = {"error": "Invalid JSON"}
                        else:
                            results[url] = {
                                "error": f"Status code {response.status}"}
                except asyncio.TimeoutError:
                    results[url] = {"error": "Timeout"}
                except Exception as e:
                    results[url] = {"error": str(e)}

        tasks = [process_url(url) for url in urls]
        await asyncio.gather(*tasks)

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                for url, data in results.items():
                    f.write(
                        json.dumps({"url": url, "data": data},
                                   ensure_ascii=False)
                        + "\n"
                    )
        except Exception:
            pass


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        sys.exit(1)

    input_file = sys.argv[1]
    asyncio.run(fetch_urls(input_file))
