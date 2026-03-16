from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from database import get_db
import models

router = APIRouter(tags=["Interfaccia Web"])

# Diciamo a questo router dove sono i file HTML
templates = Jinja2Templates(directory="templates")

@router.get("/table/", response_class=HTMLResponse)
def read_datasets_table(request: Request, db: Session = Depends(get_db)):
    datasets = db.query(models.Dataset).all()
    return templates.TemplateResponse(
        "index.html", {"request": request, "datasets": datasets}
    )

@router.get("/search/", response_class=HTMLResponse)
def search_datasets(request: Request, q: Optional[str] = None, db: Session = Depends(get_db)):
    if q:
        datasets = db.query(models.Dataset).filter(
            or_(
                models.Dataset.name.like(f"%{q}%"),
                models.Dataset.description.like(f"%{q}%")
            )
        ).all()
    else:
        datasets = db.query(models.Dataset).all()
    
    # Restituiamo solo un pezzetto di HTML (per HTMX!)
    return templates.TemplateResponse(
        "partials/dataset_rows.html", {"request": request, "datasets": datasets}
    )