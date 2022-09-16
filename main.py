import http
from typing import List
import uvicorn
from fastapi import Depends, FastAPI, HTTPException,Response, status
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine
import os
import json

from fastapi import File, UploadFile

models.Base.metadata.create_all(bind=engine)

app = FastAPI()



# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"go to ":"http://127.0.0.1:8000/docs"}

@app.get("/projects/", response_model=List[schemas.Project])
def read_projects(db: Session = Depends(get_db)):
    projects = crud.get_projects(db)
    return projects


@app.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(id: int, db: Session = Depends(get_db)):
    db_project = crud.get_project(db, id=id)
    if db_project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return db_project


@app.get("/experiments/", response_model=List[schemas.Experiment])
def read_experiments(db: Session = Depends(get_db)):
    experiment = crud.get_experiments(db)
    return experiment


@app.post("/projects/{project_id}/experiments/",status_code=status.HTTP_201_CREATED, response_model=schemas.Experiment)
def create_exp_under_project(project_id: int, experiment: schemas.ExperimentCreate, db: Session = Depends(get_db)):
    
    db_exp = crud.get_exp_by_name(db, id=project_id, name=experiment.experiment_name)
    
    if db_exp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"exp with name {experiment.experiment_name} already exists")
    

    return crud.create_project_experiment(db=db, experiment=experiment, project_id=project_id)

@app.post("/projects/", status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, experiment: schemas.ExperimentCreate, db: Session = Depends(get_db)):
    db_project = crud.get_project_by_name(db, name=project.project_name)
    
    if db_project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"project with name {project.project_name} already exists")
    
    proj=  crud.create_project(db=db, project=project)
    projname = proj.project_name
    os.mkdir(f'projects/{projname}')
    pid =  proj.project_id
    
    crud.create_project_experiment(db=db, experiment=experiment, project_id=pid)

    return pid


@app.put("/experiments/config/step1")
def create_config_file(project_id:int,expno:int,model_type:str, model_domain:str, db: Session = Depends(get_db)):
    #when do you update config to true
    experiment_name = db.query(models.Experiment).filter(models.Experiment.experiment_no == expno).first()
    experiment_name = experiment_name.experiment_name

    project_name = db.query(models.Project).filter(models.Project.project_id == project_id).first()
    project_name = project_name.project_name

    dir = f'projects/{project_name}/{experiment_name}'
    FILE = dir + '/file.json'
    DATA = {}
    DATA["model type"] = model_type
    DATA["model domain"] = model_domain
    DATA = json.dumps(DATA)
    _ = open(FILE, mode='w+').write(DATA)

    with open(FILE) as file:
        result = json.load(file)

    add_path = crud.update_config(expno=expno, db=db, experiment_name = experiment_name,project_name = project_name )
    return "configured"

@app.post("/experiments/config/step2/upload_model", status_code  = status.HTTP_202_ACCEPTED)
async def upload_file2(project_id:int, experiment_no:int, uploaded_file: UploadFile = File(...), db:Session = Depends(get_db)):
    experiment_name = db.query(models.Experiment).filter(models.Experiment.experiment_no == experiment_no).first()
    experiment_name = experiment_name.experiment_name

    project_name = db.query(models.Project).filter(models.Project.project_id == project_id).first()
    project_name = project_name.project_name

    file_location = f"projects/{project_name}/{experiment_name}/{uploaded_file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(uploaded_file.file.read())
    return {"info": f"file '{uploaded_file.filename}' saved at '{file_location}'"}

@app.post("/experiments/config/step2/upload_model.py")
async def upload_file2(project_id:int, experiment_no:int, uploaded_file: UploadFile = File(...), db:Session = Depends(get_db)):
    experiment_name = db.query(models.Experiment).filter(models.Experiment.experiment_no == experiment_no).first()
    experiment_name = experiment_name.experiment_name

    project_name = db.query(models.Project).filter(models.Project.project_id == project_id).first()
    project_name = project_name.project_name
    file_location = f"projects/{project_name}/{experiment_name}/{uploaded_file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(uploaded_file.file.read())
    return f"file '{uploaded_file.filename}' saved."

@app.post("/experiments/config/step2/upload_data")
async def upload_file2(project_id:int, experiment_no:int, uploaded_file: UploadFile = File(...), db:Session = Depends(get_db)):
    experiment_name = db.query(models.Experiment).filter(models.Experiment.experiment_no == experiment_no).first()
    experiment_name = experiment_name.experiment_name

    project_name = db.query(models.Project).filter(models.Project.project_id == project_id).first()
    project_name = project_name.project_name

    file_location = f"projects/{project_name}/{experiment_name}/{uploaded_file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(uploaded_file.file.read())
    return f"file '{uploaded_file.filename}' saved."



if __name__ =="__main__":
    uvicorn.run(app,host= "localhost" , port = 8000)