from app.services.postgres.config import DBConnectionHandler
from app.services.postgres.entities import GeometryModel
from geoalchemy2.shape import from_shape

class GeometryRepository:

    @classmethod
    def insert_geometries(cls, geometries: list, features: list, file_id: int):
        db_connection = DBConnectionHandler()
        try:
            with db_connection as conn:
                session = conn.session
                new_geometries = []

                for feat, geom in zip(features, geometries):
                    geometry_wkb = from_shape(geom, srid=4326)
                    new_geometry = GeometryModel(
                        geometry=geometry_wkb,
                        features=feat,
                        file_id=file_id
                    )
                    session.add(new_geometry)
                    new_geometries.append(new_geometry)

                session.commit()
                return new_geometries

        except Exception as e:
            session.rollback()
            raise e

        finally:
            session.close()
