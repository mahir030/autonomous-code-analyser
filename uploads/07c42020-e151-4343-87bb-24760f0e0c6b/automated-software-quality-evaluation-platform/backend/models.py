from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    overall_score = Column(Float)

    files = relationship("FileRecord", back_populates="project")


class FileRecord(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    filename = Column(String(255))
    language = Column(String(100))
    score = Column(Float)

    project = relationship("Project", back_populates="files")

