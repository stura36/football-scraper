from sqlalchemy import create_engine, text
from sqlalchemy.dialects import postgresql
import pandas as pd
from dotenv import load_dotenv
import os
from datetime import datetime
import sys


def get_existing_columns(engine):
    """
    Fetches the column names from the players table in the database
    """
    with engine.connect() as conn:
        query = text(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'players';
            """
        )
        result = conn.execute(query)
        columns = [row[0] for row in result]
        return columns


def prepare_df(df):
    """
    Prepares the dataframe for upserting into the database
    Checks if the columns in the dataframe are in the players table
    Changes the date of birth format to YYYY-MM-DD
    Changes the column name "City of birth" to "Place of birth"
    """

    columns = get_existing_columns(engine)

    columns_to_keep = []

    if "City of birth" in df.columns:
        df.rename(columns={"City of birth": "Place of birth"}, inplace=True)

    for column in df.columns:
        if column in columns:
            columns_to_keep.append(column)

    df["date_temp"] = pd.to_datetime(
        df["Date of birth"], format="%d.%m.%Y", errors="coerce"
    )
    df.loc[df["date_temp"].isna(), "date_temp"] = df["Date of birth"]
    df["Date of birth"] = df["date_temp"]
    df.drop(columns=["date_temp"], inplace=True)

    return df[columns_to_keep]


def pg_upsert(df, engine):
    """
    Upserts the dataframe into the players table in the database
    """

    with engine.connect() as conn:

        for row in df.iterrows():
            values = row[1].to_dict()
            keys_spaces = values.keys()
            values = {k.replace(" ", "_"): v for k, v in values.items()}
            keys_under = values.keys()

            for k, v in values.items():
                if pd.isna(v):
                    values[k] = None

            insert_into = [f'"{k}"' for k in keys_spaces]
            insert_into = ", ".join(insert_into)
            insert_values = [f":{k}" for k in keys_under]
            insert_values = ", ".join(insert_values)

            update_set = [f'"{k1}" = :{k2}' for k1, k2 in zip(keys_spaces, keys_under)]
            update_set = ",\n".join(update_set)

            query = text(
                f"""
            INSERT INTO players ({insert_into})
            VALUES ({insert_values})
            ON CONFLICT ("Full name", "Date of birth")
            DO UPDATE SET
            {update_set};
            """
            )

            conn.execute(query, values)

        time_stamp = datetime.now()
        updated_players = df.shape[0]
        query = text(
            f"""
            INSERT INTO players_log ("Update timestamp", "Number of updated players")
            VALUES (:time_stamp, :updated_players);
            """
        )
        conn.execute(
            query, {"time_stamp": time_stamp, "updated_players": updated_players}
        )
        conn.commit()


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
    players_path = sys.argv[1]

    players_df = pd.read_csv(players_path, delimiter=";")

    pg_upsert(prepare_df(players_df), engine)

    engine.dispose()
