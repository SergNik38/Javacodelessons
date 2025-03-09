import asyncio
import aiohttp
import json

urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url",
]


async def fetch_urls(urls: list[str], file_path: str, slice_size: int = 100) -> list[dict]:
    semaphore = asyncio.Semaphore(5)
    all_results = []

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:

        async def process_url(url):
            async with semaphore:
                try:
                    async with session.get(url, timeout=10) as response:
                        return {"url": url, "status_code": response.status}
                except Exception:
                    return {"url": url, "status_code": 0}

        with open(file_path, "w") as f:
            for i in range(0, len(urls), slice_size):
                url_slice = urls[i:i + slice_size]
                slice_results = await asyncio.gather(*[process_url(url) for url in url_slice])
                for result in slice_results:
                    f.write(json.dumps(result) + "\n")
                all_results.extend(slice_results)

        return all_results


if __name__ == "__main__":
    asyncio.run(fetch_urls(urls, "./results.json"))
