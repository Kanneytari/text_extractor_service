from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import httpx
from bs4 import BeautifulSoup
import asyncio
import undetected_chromedriver as uc
from fake_headers import Headers
from fake_useragent import UserAgent

app = FastAPI()

class URLRequest(BaseModel):
    url: HttpUrl

def _fetch_with_browser(url: str) -> str:
    ua = UserAgent().random
    headers = Headers().generate()
    headers["User-Agent"] = ua

    options = uc.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument(f"--user-agent={ua}")

    driver = uc.Chrome(options=options)
    try:
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd("Network.setExtraHTTPHeaders", {"headers": headers})
        driver.get(url)
        return driver.page_source
    finally:
        driver.quit()


@app.post("/extract")
async def extract_text(req: URLRequest):
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(str(req.url))
            response.raise_for_status()
            html = response.text
    except httpx.HTTPError:
        try:
            html = await asyncio.to_thread(_fetch_with_browser, str(req.url))
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(separator="\n", strip=True)
    return {"text": text}
