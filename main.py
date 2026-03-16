from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base, SessionLocal
from models import Modality
from enums import ModalityType
from routers import api, web

# 1. CREAZIONE TABELLE
# Diciamo al database: "Guarda i modelli che abbiamo definito e crea le tabelle se mancano"
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Research Data Catalog")

# 2. CONFIGURAZIONE CORS
# Questo permette alla tua app di parlare con altri siti o servizi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. SEEDING (Il setup iniziale)
# Una funzione per riempire la dispensa se è vuota al primo avvio
def init_db():
    db = SessionLocal()
    try:
        if db.query(Modality).count() == 0:
            print("Dispensa vuota, aggiungo le modalità BIDS...")
            modalities = [Modality(name=m) for m in ModalityType]
            db.add_all(modalities)
            db.commit()
    finally:
        db.close()

init_db()

# 4. AGGANCIO DEI ROUTER
# Qui diciamo all'app di usare i "camerieri" che abbiamo creato nei file separati
app.include_router(api.router)
app.include_router(web.router)

@app.get("/")
def root():
    return {"status": "Running", "message": "Benvenuti nel Catalogo Dati della Ricerca"}