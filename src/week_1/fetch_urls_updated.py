import asyncio
import json
from pathlib import Path

import aiohttp


async def fetch_urls(input_file: str) -> None:
    output_file = "result.jsonl"
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)

    url_queue = asyncio.Queue()

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

    async def worker():
        while True:
            try:
                url = await url_queue.get()
                result = await get_url(session, url)
                if result:
                    async with output_lock:
                        with open(output_file, "a", encoding="utf-8") as f:
                            f.write(json.dumps(result, ensure_ascii=False) + "\n")
                url_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Ошибка в worker: {e}")
                url_queue.task_done()

    output_lock = asyncio.Lock()

    try:
        with open(input_file) as f:
            for line in f:
                url = line.strip()
                if url:
                    await url_queue.put(url)
        print(f"URL-адреса загружены в очередь")
    except Exception as e:
        print(f"Ошибка чтения файла {input_file}: {e}")
        return

    with open(output_file, "w", encoding="utf-8"):
        pass

    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False, limit=100),
        timeout=aiohttp.ClientTimeout(total=300),
    ) as session:
        worker_count = 20
        workers = [asyncio.create_task(worker()) for _ in range(worker_count)]

        await url_queue.join()

        for w in workers:
            w.cancel()

        await asyncio.gather(*workers, return_exceptions=True)

    print("Обработка завершена")


def main():
    import sys

    if len(sys.argv) > 1:
        asyncio.run(fetch_urls(sys.argv[1]))


if __name__ == "__main__":
    main()
