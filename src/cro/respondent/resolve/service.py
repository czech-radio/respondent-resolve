# -*- coding: utf-8 -*-

import sys
import datetime as dt

from typing import List, Set
import pandas as pd
import pandas.io.sql as sqlio
import psycopg2 as db
from loguru import logger


from pandas import DataFrame
from cro.respondent.resolve.domain import Respondent, Person
from timeit import default_timer
from pathlib import Path

# path to a new xml entries

__all__ = tuple(
    [
        "load_respondents",
        "load_persons",
        "create_connection_db",
        "extract_respodents_from_df",
        "compare_persons_to_respondents",
        "respondents",
        "persons",
    ]
)


# glob memory storage init
respondents = []
persons = []


def extract_respodents_from_df(dataframe: pd.DataFrame) -> List[Respondent]:

    respondents_raw = dataframe.values.tolist()

    for line in respondents_raw:
        if line[0] == "contact":
            try:
                respondents.append(
                    Respondent(
                        openmedia_id=line[20],
                        given_name=line[19],
                        family_name=line[22],
                        labels=line[23],
                        gender=line[24],
                        foreigner=line[25],
                        affiliation=line[26],
                        matching_ids=[""],
                    )
                )
            except TypeError:
                print(f"Error parsing contact {line[0]}")

    return respondents_raw


def fetch_respondents(year: int, week_number: int) -> pd.DataFrame:

    working_directory = f"/mnt/R/GŘ/Strategický rozvoj/Kancelář/Analytics/Source/{year}"
    PATH = Path(working_directory)
    FULL_PATH = PATH / f"DATA_{year}W{week_number}_TEST.xlsx"

    df = pd.read_excel(
        FULL_PATH,
        sheet_name=0,
        header=None,
        engine="openpyxl",
    )

    df = normalize_persons(df)
    print(f"Loaded {len(df)} respondents.")

    # print(f"Normalizing dataframe")
    # ...

    return respondents


def load_respondents(year: int, week_number: int) -> List[Respondent]:

    working_directory = f"/mnt/R/GŘ/Strategický rozvoj/Kancelář/Analytics/Source/{year}"
    PATH = Path(working_directory)
    FULL_PATH = PATH / f"DATA_{year}W{week_number}_TEST.xlsx"

    df = pd.read_excel(
        FULL_PATH,
        sheet_name=0,
        header=None,
        engine="openpyxl",
    )

    df = extract_respodents_from_df(df)
    print(f"Loaded {len(df)} respondents.")

    # print(f"Normalizing dataframe")
    # ...

    return respondents


def create_connection_db(connection_str: str):
    with db.connect(connection_str) as connection:
        return connection


# ioutputs list of reposndent
def load_persons(connection) -> List[Person]:
    try:
        logger.info("Loading respondent database started")
        persons = sqlio.read_sql_query(
            f"select * from get_persons(some_date => '{dt.datetime.today().strftime('%Y-%m-%d')}')",
            connection,
        )
        logger.info("Fetch respondents finished")

        return persons.values.tolist()

    except Exception as ex:
        logger.error(ex)
        raise ex


# outputs pandas dataframe
def fetch_persons(connection) -> pd.DataFrame:
    try:
        logger.info("Loading respondent database started")
        persons = sqlio.read_sql_query(
            f"select * from get_persons(some_date => '{dt.datetime.today().strftime('%Y-%m-%d')}')",
            connection,
        )
        logger.info("Fetch respondents finished")

        return persons

    except Exception as ex:
        logger.error(ex)
        raise ex


def compare_persons_to_respondents(
    respondents: List[Respondent], persons: List[Person]
):

    # convert lists to dataframes
    respondents_df = pd.DataFrame([x.asdict() for x in respondents])
    persons_df = pd.DataFrame([x.asdict() for x in persons])

    # normalize both data
    respondents_df = normalize_persons(respondents_df)
    persons_df = normalize_persons(persons_df)

    # compare dataframes
    modified = identify_respondents(
        respondents=respondents_df, known_persons=persons_df
    )
    return modified

    # variant 1 use match_function
    # for item in respondents:
    #    resolved_df = match_persons(respondent=item, persons=persons_df)
    #    if(resolved_df is not None):
    #        for x in resolved_df:
    #            item.add_matching_id(x.uuid)
    #            count = count + 1

    # variant 2 compare lists directly
    # for respondent in respondents:
    #    for person in persons:
    #        if(respondent.given_name==person.given_name &&
    #                respondent.family_name==person.family_name &&
    #                respondent.affiliation==person.affiliation
    #                ):
    #            respondent.add_matching_id(respondent.uuid)
    # print(f"Found {count} matches.")


# paste from cro-respodent-match


def normalize_persons(persons: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the person data.
    :param persons: The input data with person data.
        Columns:
            openmedia_id: UUID, dtype: str
            given_name: String, dtype: str
            family_name: String, dtype: str
            affiliation: String, dtype: str
            labels: String, dtype: str
            gender: Integer, dtype: int (0, 1, 2)
            foreigner: Integer, dtype: int (0, 1, 2)
    :return: The normalized copy of original person data.
    """

    # df = pd.DataFrame([x.asdict() for x in persons])

    # Get only subset of columns.
    df = persons[
        [
            "openmedia_id",
            "given_name",
            "family_name",
            "affiliation",
            "gender",
            "labels",
            "foreigner",
            "matching_ids",
        ]
    ].copy()

    # Clean (lowercase and strip) the columns and set the appropriate type.

    df.given_name = df.given_name.astype(str)
    df.given_name = df.given_name.str.strip()
    df.given_name = df.given_name.str.lower()

    df.family_name = df.family_name.astype(str)
    df.family_name = df.family_name.str.strip()
    df.family_name = df.family_name.str.lower()

    df.affiliation = df.affiliation.astype(str)
    df.affiliation = df.affiliation.str.strip()
    df.affiliation = df.affiliation.str.lower()

    df.labels = df.labels.astype(str)
    df.labels = df.labels.str.strip()
    df.labels = df.labels.str.lower()
    df.labels = (
        df.labels.str.split(";")
        .apply(list)
        .map(lambda lst: list(map(str.strip, lst)))
        .map(lambda lst: [x for x in lst if x != ""])
        .apply(set)
    )

    df.openmedia_id = df.openmedia_id.astype(str)
    df.openmedia_id = df.openmedia_id.str.strip()

    df.gender = df.gender.astype(str)
    df.gender = df.gender.str.replace("1", "male")
    df.gender = df.gender.str.replace("2", "female")
    df.gender = df.gender.str.replace("0", "unknown")

    # df.foreigner: 0, 1, 2

    return df


# @task
def match_persons(
    respondent: Respondent, persons: pd.DataFrame, match_labels=False, strategy=None
) -> pd.DataFrame:
    """
    Match the given respondent with registered persons and return a table of similar persons.
    The respondent matches the person if the name, party and any label matches.
    """
    import re

    # 1. Transform respondent attributes for matching.

    respondent_given_name: str = respondent.given_name.strip().lower()
    respondent_family_name: str = respondent.family_name.strip().lower()
    respondent_affiliation: str = respondent.affiliation.strip().lower()
    respondent_labels: Set[str] = set([x.strip().lower() for x in respondent.labels])

    # 2. Match the given respondent with persons.

    # Get the persons which matches with name and party.
    matching_persons = persons[
        (persons.given_name == respondent_given_name)
        & (persons.family_name == respondent_family_name)
        & (persons.affiliation == respondent_affiliation)
    ]
    # Get the persons which match at least in one label.
    if match_labels:
        matching_persons = matching_persons[
            matching_persons.labels.apply(
                lambda x: any(item for item in respondent_labels if item in x)
            )
        ]

    return matching_persons


# @task
def modify_respondents(respondents: pd.DataFrame) -> pd.DataFrame:
    respondents.fillna("", inplace=True)
    respondents["labels"] = respondents["labels"].str.split(";")
    return respondents


# @task
def identify_respondents(respondents: pd.DataFrame, known_persons):
    """
    Identify (match) respondents against known persons.
    """
    start = default_timer()
    index = 0
    identified = 0
    candidates_final = []
    for i, candidate in respondents.iterrows():
        # if index >= 1: break # DEBUG
        respondent = Respondent(
            openmedia_id=candidate.openmedia_id,
            given_name=candidate.given_name,
            family_name=candidate.family_name,
            affiliation=candidate.affiliation,
            labels=candidate.labels,
            gender=candidate.gender,
            foreigner=candidate.foreigner,
            matching_ids=[""],
        )
        found = match_persons(respondent, known_persons, match_labels=True)

        if len(found):
            identified += 1
        index += 1

        person_ids = found.openmedia_id.to_list() if len(found) else ["None"]
        person_ids = ";".join(person_ids)
        candidates_final.append(person_ids)

        sys.stdout.write(
            f"\rIdentified {identified} from {index}/{len(respondents)} candidates in {default_timer() - start} seconds"
        )
        sys.stdout.flush()

    final = respondents.assign(matching_ids=candidates_final)

    return final
