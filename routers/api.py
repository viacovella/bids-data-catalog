from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importiamo i nostri pezzi dai file creati prima
from database import get_db
import models, schemas

router = APIRouter(
    prefix="/datasets", # Tutti gli indirizzi inizieranno con /datasets
    tags=["API Datasets"] # Serve per organizzare la documentazione automatica
)

@router.get("/", response_model=List[schemas.DatasetRead])
def read_datasets(db: Session = Depends(get_db)):
    return db.query(models.Dataset).all()

@router.post("/", response_model=schemas.DatasetRead)
def create_dataset(dataset: schemas.DatasetCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Dataset).filter(
        (models.Dataset.name == dataset.name) | (models.Dataset.uri == dataset.uri)
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Dataset already exists.")

    # Cerchiamo le modalità nel DB usando i nomi inviati dall'utente
    modality_objects = db.query(models.Modality).filter(
        models.Modality.name.in_(dataset.modalities)
    ).all()
    
    db_dataset = models.Dataset(
        **dataset.model_dump(exclude={"modalities"}),
        modalities=modality_objects
    )
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

# ... qui andrebbero anche PATCH e DELETE seguendo la stessa logica