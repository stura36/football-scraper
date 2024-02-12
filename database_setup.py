from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os


def create_player_table(engine):
    """
    Creates the players table in the database
    """

    with engine.connect() as conn:
        query = text("""CREATE EXTENSION IF NOT EXISTS "uuid-ossp";""")
        conn.execute(query)
        conn.commit()

        query1 = text(
            """
        CREATE TABLE IF NOT EXISTS players (
            "PlayerID" UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
            "URL" TEXT,
            "Name" TEXT,
            "Full name" TEXT,
            "Date of birth" DATE,
            "Age" INTEGER,
            "Place of birth" TEXT,
            "Country of birth" TEXT,
            "Position" TEXT,
            "Current club" TEXT,
            "National team" TEXT,
            "Appearance count" INTEGER,
            "Goal count" INTEGER,
            "Scrap timestamp" TIMESTAMP,
            UNIQUE("Full name", "Date of birth")
        );
        """
        )
        conn.execute(query1)
        query2 = text(
            """
            CREATE TABLE IF NOT EXISTS players_log(
            "Update timestamp" TIMESTAMP,
            "Number of updated players" INTEGER
        );
        """
        )
        conn.execute(query2)
        conn.commit()

    return


if __name__ == "__main__":
    load_dotenv()

    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_name = os.getenv("DB_NAME")

    engine = create_engine(
        f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )

    create_player_table(engine)

    engine.dispose()
