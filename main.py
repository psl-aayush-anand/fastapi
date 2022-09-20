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

from fastapi.middleware.cors import CORSMiddleware



origins = ['*']


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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


@app.put("/experiments/config/step1", status_code=status.HTTP_202_ACCEPTED)
def create_config_file(expno:int ,model : schemas.CreateConfigFile, db: Session = Depends(get_db)):
    
    experiment = db.query(models.Experiment).filter(models.Experiment.experiment_no == expno).first()
    experiment_name = experiment.experiment_name

    project_name = db.query(models.Project).filter(models.Project.project_id == experiment.project_id).first()
    project_name = project_name.project_name

    dir = f'projects/{project_name}/{experiment_name}'
    FILE = dir + '/file.json'

    DATA = crud.create_config_file(db=db,model=model)

    DATA = json.dumps(DATA)
    _ = open(FILE, mode='w+').write(DATA)

    with open(FILE) as file:
        result = json.load(file)

    

    add_path = crud.update_config_path(expno=expno, db=db, dir=FILE )
    return "configured"

@app.post("/experiments/config/step2/upload_file1", status_code  = status.HTTP_202_ACCEPTED)
async def upload_file1(experiment_no:int, uploaded_file: UploadFile = File(...), db:Session = Depends(get_db)):
    return crud.save_file(db=db,experiment_no=experiment_no, uploaded_file=uploaded_file)

@app.post("/experiments/config/step2/upload_file2", status_code=status.HTTP_202_ACCEPTED)
async def upload_file2(experiment_no:int, uploaded_file: UploadFile = File(...), db:Session = Depends(get_db)):
    return crud.save_file(db=db,experiment_no=experiment_no,uploaded_file=uploaded_file)

@app.post("/experiments/config/step2/upload_file3", status_code=status.HTTP_202_ACCEPTED)
async def upload_file3(experiment_no:int, uploaded_file: UploadFile = File(...), db:Session = Depends(get_db)):
    return crud.save_file(db=db,experiment_no=experiment_no, uploaded_file=uploaded_file)

@app.post("/experiments/uploads/", status_code=status.HTTP_202_ACCEPTED)
async def upload_file3(experiment_no:int, uploaded_file1: UploadFile = File(...), uploaded_file2: UploadFile = File(...), uploaded_file3: UploadFile = File(...), db:Session = Depends(get_db)):
    crud.save_file(db=db,experiment_no=experiment_no, uploaded_file=uploaded_file1)
    crud.save_file(db=db,experiment_no=experiment_no, uploaded_file=uploaded_file2)
    crud.save_file(db=db,experiment_no=experiment_no, uploaded_file=uploaded_file3)
    return 'files saved'

@app.put("/experiments/config/step3/", status_code=status.HTTP_200_OK)
def generate_uuid(expno :int, db: Session = Depends(get_db)):
    
    exp_uuid = db.query(models.Experiment).filter(models.Experiment.experiment_no == expno).first()
    exp_uuid = exp_uuid.uuid

    config_path = crud.update_configuration(expno=expno, db=db)

    return exp_uuid


@app.delete("/experiments/delete_experiment/", status_code=status.HTTP_200_OK)
def delete_experiment(exp_id: int, db:Session = Depends(get_db)):
    db_exp = db.query(models.Experiment).get(exp_id)

    if not db_exp:
        raise HTTPException(status_code=404, detail="Experiment not found")

    
    return crud.delete_experiment(db=db, exp_id=exp_id)

@app.delete("/projects/delete_project/", status_code=status.HTTP_200_OK)
def delete_project(proj_id: int, db:Session = Depends(get_db)):
    db_proj = db.query(models.Project).get(proj_id)

    if not db_proj:
        raise HTTPException(status_code=404, detail="Project not found")

    return crud.delete_project(db=db, proj_id=proj_id)




if __name__ =="__main__":
    uvicorn.run(app,host= "localhost" , port = 8000)