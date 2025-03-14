from app.services.postgres.config import DBConnectionHandler
from app.services.postgres.entities import FilesModel

class FileRepository:

    @classmethod
    def insert_file(cls, name: str):
        with DBConnectionHandler() as db_connection:
            try:
                new_file = FilesModel(name=name)
                db_connection.session.add(new_file)
                db_connection.session.commit()

                return FilesModel(
                    id=new_file.id,
                    name=new_file.name
                )
            except:
                db_connection.session.rollback()
                raise

