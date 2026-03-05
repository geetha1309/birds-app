from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Birds of Wonder")
templates = Jinja2Templates(directory="app/templates")

Instrumentator().instrument(app).expose(app)

BIRDS = [
    {
        "name": "Kingfisher",
        "scientific": "Alcedo atthis",
        "fact": "Dives like a tiny torpedo to catch fish.",
        "region": "Europe & Asia",
        "img": "https://images.unsplash.com/photo-1544551763-ced9ff386a54?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Puffin",
        "scientific": "Fratercula arctica",
        "fact": "Can hold multiple fish in its beak using spines on the tongue.",
        "region": "North Atlantic",
        "img": "https://images.unsplash.com/photo-1501706362039-c6e13d3f2b45?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Hummingbird",
        "scientific": "Trochilidae",
        "fact": "Beats wings up to ~80 times per second and can hover.",
        "region": "Americas",
        "img": "https://images.unsplash.com/photo-1465153690352-10c1b29577f8?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Snowy Owl",
        "scientific": "Bubo scandiacus",
        "fact": "Often hunts in daylight and has excellent hearing.",
        "region": "Arctic",
        "img": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1200&q=80",
    },
    {
        "name": "Scarlet Macaw",
        "scientific": "Ara macao",
        "fact": "Strong beak can crack hard nuts; highly social and intelligent.",
        "region": "Central & South America",
        "img": "https://images.unsplash.com/photo-1525253086316-d0c936c814f8?auto=format&fit=crop&w=1200&q=80",
    },
]


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "birds": BIRDS})

@app.get("/healthz")
def healthz():
    return {"ok": True}

@app.get("/api/birds")
def api_birds():
    return {"birds": BIRDS}