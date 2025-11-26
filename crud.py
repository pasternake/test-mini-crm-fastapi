from sqlalchemy.orm import Session
from sqlalchemy import func
import models, schemas
import random

def get_operator(db: Session, operator_id: int):
    return db.query(models.Operator).filter(models.Operator.id == operator_id).first()

def get_operators(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Operator).offset(skip).limit(limit).all()

def create_operator(db: Session, operator: schemas.OperatorCreate):
    db_operator = models.Operator(name=operator.name, is_active=operator.is_active, load_limit=operator.load_limit)
    db.add(db_operator)
    db.commit()
    db.refresh(db_operator)
    return db_operator

def update_operator(db: Session, operator_id: int, is_active: bool = None, load_limit: int = None):
    db_operator = get_operator(db, operator_id)
    if not db_operator:
        return None
    if is_active is not None:
        db_operator.is_active = is_active
    if load_limit is not None:
        db_operator.load_limit = load_limit
    db.commit()
    db.refresh(db_operator)
    return db_operator

def get_source(db: Session, source_id: int):
    return db.query(models.Source).filter(models.Source.id == source_id).first()

def create_source(db: Session, source: schemas.SourceCreate):
    db_source = models.Source(name=source.name)
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

def set_source_allocations(db: Session, source_id: int, allocations: list[schemas.AllocationSet]):
    # Clear existing
    db.query(models.SourceOperatorLink).filter(models.SourceOperatorLink.source_id == source_id).delete()
    
    links = []
    for alloc in allocations:
        link = models.SourceOperatorLink(source_id=source_id, operator_id=alloc.operator_id, weight=alloc.weight)
        links.append(link)
    
    db.add_all(links)
    db.commit()
    return links

def get_or_create_lead(db: Session, identifier: str):
    lead = db.query(models.Lead).filter(models.Lead.identifier == identifier).first()
    if not lead:
        lead = models.Lead(identifier=identifier)
        db.add(lead)
        db.commit()
        db.refresh(lead)
    return lead

def select_operator(db: Session, source_id: int):
    # 1. Get all operators for this source
    links = db.query(models.SourceOperatorLink).filter(models.SourceOperatorLink.source_id == source_id).all()
    
    candidates = []
    weights = []
    
    for link in links:
        op = link.operator
        # 2. Filter active
        if not op.is_active:
            continue
            
        # 3. Check load
        current_load = db.query(func.count(models.Interaction.id)).filter(
            models.Interaction.operator_id == op.id,
            models.Interaction.status == "OPEN"
        ).scalar()
        
        if current_load < op.load_limit:
            candidates.append(op)
            weights.append(link.weight)
    
    if not candidates:
        return None
        
    # 4. Weighted random selection
    # If all weights are 0, use equal probability (or handle as edge case)
    if sum(weights) == 0:
         return random.choice(candidates)

    selected = random.choices(candidates, weights=weights, k=1)[0]
    return selected

def create_interaction(db: Session, interaction: schemas.InteractionCreate):
    lead = get_or_create_lead(db, interaction.lead_identifier)
    
    operator = select_operator(db, interaction.source_id)
    operator_id = operator.id if operator else None

    # TODO: need to understand how to handle operator_id=None case
    
    db_interaction = models.Interaction(
        lead_id=lead.id,
        source_id=interaction.source_id,
        operator_id=operator_id,
        status="OPEN"
    )
    db.add(db_interaction)
    db.commit()
    db.refresh(db_interaction)
    return db_interaction
