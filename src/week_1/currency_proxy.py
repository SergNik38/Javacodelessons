import json
from urllib.parse import unquote

import aiohttp
import uvicorn


async def fetch_currency_rate(currency: str) -> dict:
    url = f"https://api.exchangerate-api.com/v4/latest/{currency}"
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=False)
    ) as session:
        async with session.get(url) as response:
            return await response.json()


async def app(scope, receive, send):
    if scope["path"] == "/favicon.ico":
        return

    currency = unquote(scope["path"].strip("/")).upper()
    data = await fetch_currency_rate(currency)
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [[b"content-type", b"application/json"]],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": json.dumps(data).encode(),
        }
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
