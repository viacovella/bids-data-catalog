import sqlalchemy
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

# 1. Importiamo la "Base" dalla nostra dispensa
from database import Base

# 2. Importiamo le "Etichette" dal nostro dizionario
from enums import LicenseType, ModalityType

# 3. Tabella di collegamento (Il ponte)
# Nota: qui usiamo sqlalchemy.Column, sqlalchemy.ForeignKey, ecc.
dataset_modalities = sqlalchemy.Table(
    "dataset_modalities",
    Base.metadata,
    sqlalchemy.Column("dataset_id", sqlalchemy.ForeignKey("datasets.id", ondelete="CASCADE"), primary_key=True),
    sqlalchemy.Column("modality_id", sqlalchemy.ForeignKey("modalities.id", ondelete="CASCADE"), primary_key=True),
)



# 4. Modello Modality
class Modality(Base):
    __tablename__ = "modalities"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.Enum(ModalityType), unique=True, index=True)

    # Relazione con i dataset
    datasets = relationship("Dataset", secondary=dataset_modalities, back_populates="modalities")

    def __repr__(self):
        return f"<Modality(name='{self.name}')>"

# 5. Modello Dataset
class Dataset(Base):
    __tablename__ = "datasets"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, index=True)
    name = sqlalchemy.Column(sqlalchemy.String, index=True, unique=True, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String)
    participants = sqlalchemy.Column(sqlalchemy.Integer, default=0)
    license = sqlalchemy.Column(sqlalchemy.Enum(LicenseType), default=LicenseType.CC0)
    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=lambda: datetime.now(timezone.utc))
    uri = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)

    # Relazione: "Ehi, guarda nella tabella ponte per trovare le mie modalità"
    modalities = relationship("Modality", secondary=dataset_modalities, back_populates="datasets")

    def __repr__(self):
        return f"<Dataset(id={self.id}, name='{self.name}', participants={self.participants})>"