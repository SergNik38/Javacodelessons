import asyncio
import json
from pathlib import Path

import aiohttp


async def fetch_urls(input_file: str) -> None:
    output_file = "result.jsonl"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(input_file) as f:
            urls = [url.strip() for url in f if url.strip()]
    except Exception as e:
        print(f"Ошибка чтения файла {input_file}: {e}")
        return

    semaphore = asyncio.Semaphore(5)

    async def get_url(session: aiohttp.ClientSession, url: str) -> dict | None:
        async with semaphore:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.read()
                        return {"url": url, "content": json.loads(data)}
            except Exception as e:
                print(f"Ошибка {url}: {e}")
            return None

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False),
        timeout=aiohttp.ClientTimeout(total=300),
    ) as session:
        with open(output_file, "w", encoding="utf-8") as f:
            slice_size = 10
            for i in range(0, len(urls), slice_size):
                url_slice = urls[i : i + slice_size]
                tasks = [get_url(session, url) for url in url_slice]
                results = await asyncio.gather(*tasks)

                for result in results:
                    if result:
                        f.write(json.dumps(result, ensure_ascii=False) + "\n")


def main():
    import sys

    if len(sys.argv) > 1:
        asyncio.run(fetch_urls(sys.argv[1]))


if __name__ == "__main__":
    main()
