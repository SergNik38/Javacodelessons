import asyncio
import aiohttp
import json

urls = [
    "https://example.com",
    "https://httpbin.org/status/404",
    "https://nonexistent.url"
]


async def fetch_urls(urls: list[str], file_path: str) -> list[dict]:
    semaphore = asyncio.Semaphore(5)
    results = []

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        async def process_url(url):
            async with semaphore:
                try:
                    async with session.get(url, timeout=10) as response:
                        return {"url": url, "status_code": response.status}
                except Exception:
                    return {"url": url, "status_code": 0}

        results = await asyncio.gather(*[process_url(url) for url in urls])

        with open(file_path, 'w') as f:
            for result in results:
                f.write(json.dumps(result) + '\n')

        return results


if __name__ == '__main__':
    asyncio.run(fetch_urls(urls, './results.json'))
