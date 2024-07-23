from sqlalchemy import insert, create_engine, MetaData
from sqlalchemy.orm import Session
from structlog import get_logger

from db_init_data.config import get_settings


if __name__ == "__main__":
    logger = get_logger()

    logger.info("Get settings...")
    settings = get_settings()

    logger.info("Create engine...")
    engine = create_engine(
        f"postgresql+psycopg://"
        f"{settings.db_user}:{settings.db_password.get_secret_value()}"
        f"@{settings.db_host}/{settings.db_name}"
    )

    logger.info("Reflect DB tables...")
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=engine)

    category = metadata_obj.tables["category"]

    logger.info("Populate tables...")
    with Session(engine) as session:
        session.execute(
            insert(category),
            [
                {
                    "name": "Cars",
                    "description": "Some great cars"
                },
                {
                    "name": "Numbers",
                    "description": "Our favorite numbers"
                },
                {
                    "name": "Houses",
                    "description": "Some cool houses"
                }
            ]
        )

        session.commit()

    logger.info("Done!")
