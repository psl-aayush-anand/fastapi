from sqlite3 import Timestamp
from typing import List, Union

from pydantic import BaseModel


class ExperimentBase(BaseModel):
    experiment_name: str


class ExperimentCreate(ExperimentBase):
    pass


class Experiment(ExperimentBase):
    experiment_no: int
    project_id: int
    

    class Config:
        orm_mode = True


class ProjectBase(BaseModel):
    project_name: str


class ProjectCreate(ProjectBase):
    pass


class Project(ProjectBase):
    project_id: int
    
    experiments: List[Experiment] = []

    class Config:
        orm_mode = True
