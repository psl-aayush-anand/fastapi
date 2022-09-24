from distutils.command.config import config
from sqlite3 import Timestamp
from typing import List, Union

from pydantic import BaseModel

class RunConfigBase(BaseModel):
    batch_size: int
    field_1 :str
    field_2:str
    no_of_epoch: int


class CreateRunConfigFile(RunConfigBase):
    pass


class RunCreate(RunConfigBase):
    pass


class RunBase(BaseModel):
    pass


class RunCreate(BaseModel):
    pass


class Run(RunBase):
    run_no: int
    experiment_no: int
    run_name:str

    class Config:
        orm_mode = True


class ExperimentBase(BaseModel):
    experiment_name: str


class ExperimentCreate(ExperimentBase):
    pass


class Experiment(ExperimentBase):
    experiment_no: int
    project_id: int
    runs: List[Run] = []

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


class ConfigBase(BaseModel):
    model_type: str
    epxeriment_domain: str


class CreateConfigFile(ConfigBase):
    pass


