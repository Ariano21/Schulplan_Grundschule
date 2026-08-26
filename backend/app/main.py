from fastapi import FastAPI

from app.routers import auth, grunddaten, halbjahre, unterrichtseinheiten

app = FastAPI(title="Schulplan Grundschule API", version="0.1.0")

app.include_router(auth.router)
app.include_router(grunddaten.router)
app.include_router(halbjahre.router)
app.include_router(unterrichtseinheiten.router)


@app.get("/health")
def health():
    return {"status": "ok"}
