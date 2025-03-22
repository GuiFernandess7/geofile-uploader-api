from app.services.postgres.config import DBConnectionHandler
from app.services.postgres.entities import GeometryModel
from geoalchemy2.shape import from_shape

import logging


class GeometryRepository:

    @classmethod
    def insert_geometries(
        cls,
        name: str,
        geometries: list,
        features: list,
        file_id: int,
        logger: logging.Logger,
    ):
        db_connection = DBConnectionHandler()
        logger.info(f"[{name}] Adding geometries...")
        try:
            with db_connection as conn:
                session = conn.session
                new_geometries = []

                for feat, geom in zip(features, geometries):
                    geometry_wkb = from_shape(geom, srid=4326)
                    new_geometry = GeometryModel(
                        geometry=geometry_wkb, features=feat, file_id=file_id
                    )
                    session.add(new_geometry)
                    new_geometries.append(new_geometry)
                    logger.info(
                        f"[{name}] Geometries added succesfully to the database"
                    )

                session.commit()
                return new_geometries

        except Exception as e:
            session.rollback()
            raise e

        finally:
            session.close()
