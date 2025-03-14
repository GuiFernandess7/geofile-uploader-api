from app.services.postgres.base import Base
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from geoalchemy2 import Geometry

class FilesModel(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)

    geometries = relationship("GeometryModel", back_populates="file")

    def __repr__(self):
        return f"""File: [id={self.id}, name={self.name}]"""

class GeometryModel(Base):
    __tablename__ = "geometries"

    id = Column(Integer, primary_key=True)
    geometry = Column(Geometry("GEOMETRY", srid=4326), nullable=False)
    features = Column(JSONB, nullable=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False)

    file = relationship("FilesModel", back_populates="geometries")

    def __repr__(self):
        return f"Geometry: [id={self.id}, file_id={self.file_id}, geometry={self.geometry}]"