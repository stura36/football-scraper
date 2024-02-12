from sqlalchemy import create_engine, text
from sqlalchemy.dialects import postgresql
import pandas as pd
from dotenv import load_dotenv
import os
import sys
import sqlalchemy


def add_age_category(engine):
    with engine.connect() as conn:
        try:
            query = text(
                """
                    ALTER TABLE players
                    ADD COLUMN Age_category VARCHAR(10);
                """
            )
            conn.execute(query)
            conn.commit()
        except sqlalchemy.exc.ProgrammingError:
            conn.commit()
            pass

        query = text(
            """
            UPDATE players
            SET Age_category =
            CASE
                WHEN "Age" <= 23 THEN 'Young'
                WHEN "Age" > 32 THEN 'Old'
                ELSE 'MidAge'
            END;
            """
        )
        conn.execute(query)
        conn.commit()


def add_goals_per_appearance(engine):
    with engine.connect() as conn:
        try:
            query = text(
                """
                ADD COLUMN Goals_per_appearance FLOAT;
                """
            )
            conn.execute(query)
            conn.commit()
        except sqlalchemy.exc.ProgrammingError:
            conn.commit()
            pass
        query = text(
            """
        UPDATE players
        SET Goals_per_appearance = "Goal count" / NULLIF("Appearance count",0);
        """
        )
        conn.execute(query)
        conn.commit()


def calculate_metrics(engine):

    with engine.connect() as conn:
        query = text(
            """
                     SELECT "Current club" as "Club", 
                     COUNT(*) as "Total number of players", 
                     AVG("Age") as "Average age", 
                     AVG("Appearance count") as "Average appearance count"
                    FROM players
                    GROUP BY 1                  
                     """
        )
        result = conn.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

    return df


def extract_young_competition(engine, club_name):
    with engine.connect() as conn:
        query = text(
            f"""
                     SELECT "Full name" as "Player",
                     (SELECT COUNT(*) FROM players p2
                     WHERE p1."Position" = p2."Position"
                     AND p1."Appearance count" < p2."Appearance count"
                     AND p1."Age" > p2."Age") as "Young_competition"
                    FROM players p1
                    WHERE p1."Current club"='{club_name}'
            """
        )
        result = conn.execute(query)
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

    return df


def get_number_of_players(engine):
    with engine.connect() as conn:
        query = text(
            """
            SELECT COUNT(*) FROM players;
            """
        )
        result = conn.execute(query)
        number_of_players = result.fetchone()[0]

    return number_of_players


def get_number_of_clubs(engine):
    with engine.connect() as conn:
        query = text(
            """
            SELECT COUNT(DISTINCT "Current club") FROM players;
            """
        )
        result = conn.execute(query)
        number_of_clubs = result.fetchone()[0]

    return number_of_clubs


def get_last_update(engine):
    with engine.connect() as conn:
        query = text(
            """
            SELECT * FROM players_log
            ORDER BY "Update timestamp" DESC
            LIMIT 1;
            """
        )
        result = conn.execute(query)
        last_update = result.fetchone()
        return last_update[0], last_update[1]


if __name__ == "__main__":
    # Setting up connection to the database
    load_dotenv()
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_user = os.getenv("DB_USER")
    db_pass = os.getenv("DB_PASS")
    db_name = os.getenv("DB_NAME")

    engine = create_engine(
        f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    )

    # DATA enrichment
    add_age_category(engine)
    add_goals_per_appearance(engine)
    # Query 2
    club_metrics_df = calculate_metrics(engine)

    # Query 3
    club_name = sys.argv[1]
    young_comp_df = extract_young_competition(engine, club_name)
    last_update, updated_players = get_last_update(engine)

    # Print query results and additional information
    print("Total number of players in the database:", get_number_of_players(engine))
    print("Total number of clubs in the database:", get_number_of_clubs(engine))
    print("Last update:", last_update.strftime("%Y-%m-%d %H:%M:%S"))
    print("Number of players updated in the last update:", updated_players)
    print("Club metrics:")
    print(club_metrics_df)
    print("Result of third query:")
    print(young_comp_df)

    engine.dispose()
