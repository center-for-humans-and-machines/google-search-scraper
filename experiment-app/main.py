from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import httpx
from bs4 import BeautifulSoup
import json
import urllib.parse
import base64

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SEARCH_APP_URL = "http://search-app:8000/search"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html", {"results": None})

@app.post("/api/search", response_class=JSONResponse)
async def api_search(query: str = Form(...)):
    results = []
    error = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(SEARCH_APP_URL, params={"q": query})
            response.raise_for_status()
            html_results = response.text
            
            soup = BeautifulSoup(html_results, 'html.parser')
            parsed_results = []
            
            # Simple heuristic: Google often puts result titles in <h3> tags inside <a> tags
            for h3 in soup.find_all('h3'):
                a = h3.parent
                if a and a.name == 'a':
                    title = h3.get_text()
                    link = a.get('href', '')
                    
                    # Extract the actual URL from Google's redirect links by following the redirect
                    if link.startswith('/url?') or link.startswith('/goto?'):
                        full_url = f"https://www.google.com{link}"
                        try:
                            # Send a request without following redirects to get the Location header
                            redirect_response = await client.get(full_url, follow_redirects=False)
                            location = redirect_response.headers.get('Location')
                            if location:
                                link = location
                            else:
                                # Sometimes Google uses a meta refresh or JS redirect on a 200 page
                                # Let's fallback to the previous extraction logic if Location is missing
                                parsed_link = urllib.parse.urlparse(link)
                                qs = urllib.parse.parse_qs(parsed_link.query)
                                
                                target_url = link
                                if 'q' in qs:
                                    target_url = qs['q'][0]
                                elif 'url' in qs:
                                    target_url = qs['url'][0]
                                    
                                link = urllib.parse.unquote(target_url)
                        except Exception as e:
                            print(f"Error following redirect for {link}: {e}")
                            
                    parsed_results.append({'title': title, 'link': link})
            
            print(f"Parsed results: {parsed_results}", flush=True)
            results = parsed_results
    except Exception as e:
        error = str(e)
    
    return {"results": results, "error": error}
