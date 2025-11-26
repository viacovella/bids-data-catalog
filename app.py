from typing import Optional
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime, timezone

from pydantic import BaseModel, field_validator
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

import enum

app = FastAPI()

origins = ["*"] 
# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# Database setup
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


Base = declarative_base()

# Enums

class LicenseType(str, enum.Enum):
    CC_BY = "CC-BY"
    CC0 = "CC0"
    CC_BY_SA = "CC-BY-SA"
    CC_BY_NC = "CC-BY-NC"
    PDDL = "PDDL"
    ODBL = "ODBL"
    UNKNOWN = "UNKNOWN"

class ModalityType(str, enum.Enum):
    MRI = "MRI"
    EEG = "EEG"
    MEG = "MEG"
    FMRI = "fMRI"
    DTI = "DTI"
    UNKNOWN = "UNKNOWN"

# Relationships

dataset_modalities = sqlalchemy.Table(
    "dataset_modalities",
    Base.metadata,
    sqlalchemy.Column("dataset_id", sqlalchemy.ForeignKey("datasets.id", ondelete="CASCADE"), primary_key=True),
    sqlalchemy.Column("modality_id", sqlalchemy.ForeignKey("modalities.id", ondelete="CASCADE"), primary_key=True),
)

# Models

class Modality(Base):
    __tablename__ = "modalities"

    # Seeding delle modalità: MRI, EEG, MEG, fMRI, DTI


    
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.Enum(ModalityType), unique=True, index=True)

    # OPZIONALE: Se vuoi sapere quali dataset usano questa modalità
    datasets = sqlalchemy.orm.relationship("Dataset", secondary=dataset_modalities, back_populates="modalities")

    def __repr__(self):
        return f"<Modality(name='{self.name}')>"

class Dataset(Base):
    __tablename__ = "datasets"
    # id is the dataset primary key in the database
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    # name is a unique name, more like a codename. it must be unique as well
    name = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    # just a human friendly title
    description = sqlalchemy.Column(sqlalchemy.String)
    # number of participants in the dataset
    participants = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    # modalities included in the dataset (e.g., "MRI, EEG, MEG")
    modalities = sqlalchemy.orm.relationship("Modality", secondary=dataset_modalities, back_populates="datasets")
    # license under which the dataset is released
    license = sqlalchemy.Column(sqlalchemy.Enum(LicenseType), default=LicenseType.CC0)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=lambda: datetime.now(timezone.utc))
    # URI where the dataset can be accessed or downloaded
    uri = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)

    def __repr__(self):
        return f"<Dataset(id={self.id}, name='{self.name}', participants={self.participants})>"

Base.metadata.create_all(bind=engine)

# Database initialization and seeding

def init_db():
    db = SessionLocal()
    try:
        count = db.query(Modality).count()
        if count == 0:
            print ("Db is empty, seeding modalities...")
            modalities = [Modality(name=modality) for modality in ModalityType]
            db.add_all(modalities)
            db.commit()
        else:
            print("Modalities already seeded.")
    finally:
        db.close()

init_db()


# Pydantic classes

class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None
    participants: int = 0
    modalities: List[ModalityType]
    license: LicenseType = LicenseType.CC0
    uri: str

class DatasetCreate(DatasetBase):
    pass

class DatasetRead(DatasetBase):
    id: int
    created_at: datetime
    @field_validator("modalities", mode="before")
    @classmethod
    def extract_modality_names(cls, v):
       if not v:
           return []
       if hasattr(v[0], "name"):
           return [m.name for m in v]
       return v

    class Config:
        from_attributes = True

class DatasetUpdate(BaseModel):
    description: Optional[str] = None
    participants: Optional[int] = None
    modalities: Optional[List[ModalityType]] = None
    license: Optional[LicenseType] = None
    uri: Optional[str] = None





@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/datasets/", response_model=List[DatasetRead])
def read_datasets(db: Session = Depends(get_db)):
    datasets = db.query(Dataset).all()
    return datasets

@app.patch("/datasets/{dataset_id}", response_model=DatasetRead)
def update_dataset(dataset_id: int, dataset: DatasetUpdate, db: Session = Depends(get_db)):
    db_dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")

    update_data = dataset.model_dump(exclude_unset=True)

    if "modalities" in update_data:
        print ("Updating modalities...")
        modality_names = update_data.pop("modalities") # Lo togliamo dal dizionario generico e lo prendiamo in mano
        modality_objects = db.query(Modality).filter(Modality.name.in_(modality_names)).all()
        db_dataset.modalities = modality_objects # Aggiorniamo la relazione
        print (f"New modalities: {db_dataset.modalities}")

    for key, value in update_data.items():
        print (f"Updating {key} to {value}")
        setattr(db_dataset, key, value)
        print (f"{key} updated.")

    db.commit()
    db.refresh(db_dataset)
    return db_dataset

@app.post("/datasets/", response_model=DatasetRead)
def create_dataset(dataset: DatasetCreate, db: Session = Depends(get_db)):
    
    existing_dataset = db.query(Dataset).filter((Dataset.name == dataset.name) | (Dataset.uri == dataset.uri)).first()
    
    if existing_dataset:
        raise HTTPException(status_code=400, detail="Dataset with the same name or URI already exists.")

    modality_objects = db.query(Modality).filter(Modality.name.in_(dataset.modalities)).all()
    
       
      
    db_dataset = Dataset(
        name=dataset.name,
        description=dataset.description,
        participants=dataset.participants,
        license=dataset.license,
        uri=dataset.uri,
        modalities=modality_objects 
    )

    
    db.add(db_dataset)      
    db.commit()             
    db.refresh(db_dataset)  

    return db_dataset


@app.delete("/datasets/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(dataset_id: int, db: Session = Depends(get_db)):
    db_dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not db_dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    db.delete(db_dataset)
    db.commit()
    return None 


@app.get("/table/", response_class=HTMLResponse)
def read_datasets_table(request: Request, db: Session = Depends(get_db)):
    datasets = db.query(Dataset).all()
    return templates.TemplateResponse(request=request, name='index.html', context={"datasets": datasets})

