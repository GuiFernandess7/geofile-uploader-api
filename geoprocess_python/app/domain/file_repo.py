from app.services.postgres.config import DBConnectionHandler
from app.services.postgres.entities import FilesModel

import logging

class FileRepository:

    @classmethod
    def insert_file(cls, name: str, email_id: int, logger: logging.Logger):
        with DBConnectionHandler() as db_connection:
            try:
                existing_file = db_connection.session.query(FilesModel).filter_by(name=name).first()

                if existing_file:
                    logger.info(f"[{name}] -> Filename already in the database.")
                    return FilesModel(
                        id=existing_file.id,
                        name=existing_file.name,
                        email_id=email_id
                    )

                new_file = FilesModel(name=name, email_id=email_id)
                db_connection.session.add(new_file)
                db_connection.session.commit()

                logger.info(f"[{name}] -> Filename added successfully in the database.")
                return FilesModel(
                    id=new_file.id,
                    name=new_file.name,
                    email_id=email_id
                )

            except Exception as e:
                db_connection.session.rollback()
                raise e

