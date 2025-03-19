from app.services.postgres.config import DBConnectionHandler
from app.services.postgres.entities import EmailModel

import logging

class EmailRepository:

    @staticmethod
    def __email_exists(db_connection, email: str):
        existing_email = db_connection.session.query(EmailModel).filter_by(email=email).first()
        return existing_email

    @classmethod
    def insert_email(cls, email: str, logger: logging.Logger):
        with DBConnectionHandler() as db_connection:
            try:
                existing_email = cls.__email_exists(db_connection, email)

                if existing_email:
                    logger.info(f"[{email}] -> Email already exists in the database.")
                    return EmailModel(
                        id=existing_email.id,
                        email=existing_email.email
                    )

                new_email = EmailModel(email=email)
                db_connection.session.add(new_email)
                db_connection.session.commit()

                logger.info(f"[{email}] -> Email added successfully to the database.")
                return EmailModel(
                    id=new_email.id,
                    email=new_email.email
                )

            except Exception as e:
                db_connection.session.rollback()
                logger.error(f"Error while inserting email: {e}")
                raise e