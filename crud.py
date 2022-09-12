from sqlalchemy.orm import Session

import models, schemas
from models import Experiment


def get_projects(db: Session):
    return db.query(models.Project).all()


def get_project(db: Session, id: int):
    return db.query(models.Project).filter(models.Project.project_id == id).first()


def get_project_by_name(db: Session, name: str):
    return db.query(models.Project).filter(models.Project.project_name == name).first()


def create_project(db: Session, project: schemas.ProjectCreate):
    
    db_project = models.Project(**project.dict())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project


def get_experiments(db: Session):
    return db.query(models.Experiment).all()


def create_project_experiment(db: Session, experiment: schemas.ExperimentCreate, project_id: int):
    db_exp = models.Experiment(**experiment.dict(), project_id=project_id)
    db.add(db_exp)
    db.commit()
    db.refresh(db_exp)
    return db_exp







def get_experiment_by_name(db: Session, name: str, project_id: int):
    return db.query(models.Experiment).filter(models.Experiment.experiment_name == name and models.Experiment.owner_id==project_id).first()