from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, grunddaten, halbjahre, unterrichtseinheiten

app = FastAPI(title="Schulplan Grundschule API", version="0.1.0")

# Sprint-1-Scope: lokaler Vite-Dev-Server. Vor dem ersten echten Deploy auf die
# tatsächliche Frontend-Domain einschränken (siehe Architektur-Dokument, Hosting).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(grunddaten.router)
app.include_router(halbjahre.router)
app.include_router(unterrichtseinheiten.router)


@app.get("/health")
def health():
    return {"status": "ok"}
