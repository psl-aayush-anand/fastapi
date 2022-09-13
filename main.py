from typing import List
import uvicorn
from fastapi import Depends, FastAPI, HTTPException,Response, status
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine

from fastapi.middleware.cors import CORSMiddleware

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    
    return crud.create_project_experiment(db=db, experiment=experiment, project_id=project_id)




@app.post("/projects/", status_code=status.HTTP_201_CREATED)
def create_project(project: schemas.ProjectCreate, experiment: schemas.ExperimentCreate, db: Session = Depends(get_db)):
    db_project = crud.get_project_by_name(db, name=project.project_name)
    
    if db_project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"project with name {project.project_name} already exists")
    proj=  crud.create_project(db=db, project=project)
    
    pid =  proj.project_id
    
    exp = crud.create_project_experiment(db=db, experiment=experiment, project_id=pid)
    
    return pid



if __name__ =="__main__":
    uvicorn.run(app,host= "localhost" , port = 8000)