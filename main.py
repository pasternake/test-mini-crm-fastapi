from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import models, schemas, crud, database

# models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Мини-CRM Распределения Лидов")

@app.post("/operators/", response_model=schemas.Operator)
def create_operator(operator: schemas.OperatorCreate, db: Session = Depends(database.get_db)):
    return crud.create_operator(db=db, operator=operator)

@app.get("/operators/", response_model=List[schemas.Operator])
def read_operators(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return crud.get_operators(db, skip=skip, limit=limit)

@app.patch("/operators/{operator_id}", response_model=schemas.Operator)
def update_operator(operator_id: int, is_active: bool = None, load_limit: int = None, db: Session = Depends(database.get_db)):
    db_operator = crud.update_operator(db, operator_id, is_active, load_limit)
    if db_operator is None:
        raise HTTPException(status_code=404, detail="Оператор не найден")
    return db_operator

@app.post("/sources/", response_model=schemas.Source)
def create_source(source: schemas.SourceCreate, db: Session = Depends(database.get_db)):
    return crud.create_source(db=db, source=source)

@app.post("/sources/{source_id}/allocations")
def set_allocations(source_id: int, allocations: List[schemas.AllocationSet], db: Session = Depends(database.get_db)):
    return crud.set_source_allocations(db, source_id, allocations)

@app.post("/interactions/", response_model=schemas.Interaction)
def create_interaction(interaction: schemas.InteractionCreate, db: Session = Depends(database.get_db)):
    return crud.create_interaction(db=db, interaction=interaction)

@app.get("/stats/")
def get_stats(db: Session = Depends(database.get_db)):
    # Simple stats: count of interactions per operator
    operators = crud.get_operators(db)
    stats = []
    for op in operators:
        count = db.query(models.Interaction).filter(models.Interaction.operator_id == op.id).count()
        active_count = db.query(models.Interaction).filter(models.Interaction.operator_id == op.id, models.Interaction.status == "OPEN").count()
        stats.append({
            "operator": op.name,
            "total_interactions": count,
            "active_interactions": active_count,
            "limit": op.load_limit
        })
    return stats
