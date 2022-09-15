from sqlalchemy.orm import Session

import models, schemas
from models import Experiment
import os

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
    expname = db_exp.experiment_name
    
    projname = db.query(models.Project).filter(models.Project.project_id == project_id).first()
    projname = projname.project_name
    os.mkdir(f'projects/{projname}/{expname}')

    return db_exp



def update_config(db: Session, expno:int,project_name:str,experiment_name:str):   
    dir = f'projects/{project_name}/{experiment_name}/file.json'
    
    item_to_update=db.query(models.Experiment).filter(models.Experiment.experiment_no==expno).first()
    item_to_update.experiment_config_path = dir

    db.commit()

    return item_to_update

