from enum import unique
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base

from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String, unique=True, nullable=False, index=True)
    create_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    experiments = relationship("Experiment", back_populates="project")


class Experiment(Base):
    __tablename__ = "experiments"

    experiment_no = Column(Integer, primary_key=True, index=True)
    experiment_name = Column(String,nullable=False, index=True)
    create_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    project_id = Column(Integer, ForeignKey("projects.project_id", ondelete="CASCADE"))

    project = relationship("Project", back_populates="experiments")
