from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from playwright.async_api import async_playwright
import urllib.parse

app = FastAPI()

@app.get("/search", response_class=HTMLResponse)
async def search_google(q: str = Query(..., description="The search query")):
    html_content = ""
    async with async_playwright() as p:
        # Switching to Firefox to see if it bypasses the bot detection
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
        )
        page = await context.new_page()
        
        try:
            # URL encode the query
            encoded_query = urllib.parse.quote_plus(q)
            search_url = f"https://www.google.com/search?q={encoded_query}"
            
            # Go to Google
            await page.goto(search_url, wait_until="domcontentloaded")
            
            # Wait a bit for JS to render results (if necessary)
            await page.wait_for_timeout(2000) 
            
            # Get the page HTML
            html_content = await page.content()
            
        except Exception as e:
            html_content = f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>"
        finally:
            await browser.close()
            
    return html_content
