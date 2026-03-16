from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime

# Importiamo sempre i nostri Enum per la validazione
from enums import LicenseType, ModalityType

# 1. La base comune: quello che serve quasi sempre
class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None
    participants: int = 0
    modalities: List[ModalityType]
    license: LicenseType = LicenseType.CC0
    uri: str

# 2. Schema per la CREAZIONE: cosa ci deve inviare l'utente?
class DatasetCreate(DatasetBase):
    pass  # Per ora è uguale alla base

# 3. Schema per l'AGGIORNAMENTO: campi opzionali (PATCH)
class DatasetUpdate(BaseModel):
    description: Optional[str] = None
    participants: Optional[int] = None
    modalities: Optional[List[ModalityType]] = None
    license: Optional[LicenseType] = None
    uri: Optional[str] = None

# 4. Schema per la LETTURA: cosa mostriamo all'utente? (Include ID e date)
class DatasetRead(DatasetBase):
    id: int
    created_at: datetime

    # Questo pezzettino serve a "pulire" i dati che arrivano dal DB
    @field_validator("modalities", mode="before")
    @classmethod
    def extract_modality_names(cls, v):
        if not v:
            return []
        # Se riceviamo oggetti Modality dal DB, prendiamo solo il nome
        if hasattr(v[0], "name"):
            return [m.name for m in v]
        return v

    class Config:
        # Questo dice a Pydantic: "Puoi leggere i dati anche se sono oggetti del DB"
        from_attributes = True