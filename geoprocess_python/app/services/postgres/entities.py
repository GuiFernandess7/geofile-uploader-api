from app.services.postgres.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey, Enum

class FilesModel(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    name = Column(String[20], nullable=False, unique=True)

    def __repr__(self):
        return f"""File: [id={self.id}, name={self.name}]"""