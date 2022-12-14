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

import sqlite3

# path to a new xml entries

__all__ = tuple(
    [
        "load_saved_persons",
        "load_respondents",
        "load_respondents_from_file",
        "load_persons",
        "create_connection_db",
        "extract_respodents_from_df",
        "compare_respondents_to_persons",
        "get_person_by_uuid",
        "get_person_by_family_name",
        "get_person_by_full_name",
        "respondents",
        "persons",
        "resolved",
    ]
)


########################################

# glob memory storage init
respondents: List[Person] = []
persons: List[Person] = []
resolved: List[Person] = []
unmatched: List[Person] = []

# storage as dataframes
df_respondents: DataFrame
df_persons: DataFrame
df_resolved: DataFrame

#########################################


def extract_persons_from_sqlite(dataframe: pd.DataFrame) -> List[Respondent]:

    output = []

    for i, person in dataframe.iterrows():
        output.append(
            Respondent(
                openmedia_id=person.openmedia_id,
                given_name=person.given_name,
                family_name=person.family_name,
                affiliation=person.affiliation,
                labels=person.labels,
                gender=person.gender,
                foreigner=person.foreigner,
                matching_ids=[],
            )
        )

    return output


def load_saved_persons() -> List[Person]:
    con = sqlite3.connect("tmp.sqlite")
    df = pd.read_sql("select * from person", con)

    global df_persons
    df_persons = df.copy()

    global persons
    persons = extract_persons_from_sqlite(df)

    print(f"Loaded {len(persons)} persons from local database.")
    return persons


def extract_respodents_from_df(dataframe: pd.DataFrame) -> List[Respondent]:

    respondents_raw = dataframe.values.tolist()

    respondents_tmp = []

    for line in respondents_raw:
        if line[0] == "contact":
            try:
                respondents_tmp.append(
                    Respondent(
                        openmedia_id=line[20].lower(),
                        given_name=line[19].split()[1],
                        family_name=line[22],
                        labels=line[23],
                        gender=line[24],
                        foreigner=line[25],
                        affiliation=line[26],
                        matching_ids=[""],
                    )
                )
            except:
                print(f"Error parsing contact {line[0]}")

    return respondents_tmp


def extract_persons_from_df(persons: pd.DataFrame) -> List[Person]:

    output = []

    # Get only subset of columns.
    df = persons[
        [
            "unique_id",
            "given_name",
            "family_name",
            "affiliation",
            "gender",
            "labels",
            "foreigner",
        ]
    ].copy()

    for i, person in df.iterrows():
        output.append(
            Respondent(
                openmedia_id=person.unique_id,
                given_name=person.given_name,
                family_name=person.family_name,
                affiliation=person.affiliation,
                labels=person.labels,
                gender=person.gender,
                foreigner=person.foreigner,
                matching_ids=[],
            )
        )

    return output




def load_respondents(year: int, week_number: int) -> List[Respondent]:

    working_directory = f"/mnt/R/G??/Strategick?? rozvoj/Kancel????/Analytics/Source/{year}"
    PATH = Path(working_directory)
    FULL_PATH = PATH / f"DATA_{year}W{week_number}_TEST.xlsx"

    df = pd.read_excel(
        FULL_PATH,
        sheet_name=0,
        header=None,
        engine="openpyxl",
    )

    global df_respondents
    df_respondents = df

    global respondents
    respondents = extract_respodents_from_df(df)

    print(f"Loaded {len(df)} respondents.")

    return respondents


def load_respondents_from_file(filename: str | None) -> List[Respondent]:

    if filename is None:
        raise Exception("The file path must be filled-in.")

    working_directory = f"uploads/"
    PATH = Path(working_directory)
    FULL_PATH = PATH / f"{filename}"

    # if Path(FULL_PATH).is_file():
    df = pd.read_excel(
        FULL_PATH,
        sheet_name=0,
        header=None,
        engine="openpyxl",
    )

    global df_respondents
    df_respondents = df

    global respondents
    respondents = extract_respodents_from_df(df)

    print(f"Loaded {len(df)} respondents.")
    for i in respondents:
        print(i.asdict())

    return respondents



def create_connection_db(connection_str: str):
    with db.connect(connection_str) as connection:
        return connection


# outputs list of reposndent
def load_persons(connection) -> List[Person]:
    try:
        logger.info("Loading respondent database started")
        persons_tmp = sqlio.read_sql_query(
            f"select * from get_persons(some_date => '{dt.datetime.today().strftime('%Y-%m-%d')}')",
            connection,
        )
        logger.info("Fetch respondents finished")


        global df_persons
        df_persons = persons_tmp.copy()

        global persons
        persons = extract_persons_from_df(persons=persons_tmp)

        persons_to_sqlite(persons)
        return persons

    except Exception as ex:
        logger.error(ex)
        raise ex


def get_person_by_uuid(uuid: str, input_persons: List[Person]) -> List[Person]:

    output = []

    for person in input_persons:
        if person.openmedia_id == uuid:
            output.append(person)

    return output


def get_person_by_family_name(
    family_name: str, input_persons: List[Person]
) -> List[Person]:

    output = []

    for person in input_persons:
        if person.family_name == family_name:
            output.append(person)

    return output


def get_person_by_full_name(
    given_name: str, family_name: str, input_persons: List[Person]
) -> List[Person]:

    output = []

    for person in input_persons:
        if person.given_name == family_name and person.given_name == given_name:
            output.append(person)

    return output


# outputs pandas dataframe
# def fetch_persons(connection) -> pd.DataFrame:
#    try:
#        logger.info("Loading respondent database started")
#        persons = sqlio.read_sql_query(
#            f"select * from get_persons(some_date => '{dt.datetime.today().strftime('%Y-%m-%d')}')",
#            connection,
#        )
#        logger.info("Fetch respondents finished")
#
#        return persons
#
#    except Exception as ex:
#        logger.error(ex)
#        raise ex
#


def compare_name_to_persons(
    family_name: str, given_name: str, affiliation: str, input_persons: List[Person]
) -> List[Respondent]:
    output = []

    for person in input_persons:
        if (
            given_name == person.given_name
            and family_name == person.family_name
            and affiliation == person.affiliation
        ):
            output.append(person)

    return output


# TODO:
# compare and marge labels
# faster first run matching uuid only


def list_to_dataframe(input_persons: List[Person]) -> DataFrame:


    # return DataFrame.from_records([p.asdict() for p in input_persons])
    return DataFrame([p.asdict() for p in input_persons])


def compare_respondents_to_persons(
    respondents: List[Respondent], persons: List[Person]
) -> List[Respondent]:

    # convert lists to dataframes
    # respondents_df = pd.DataFrame([x.asdict() for x in respondents])
    # persons_df = pd.DataFrame([x.asdict() for x in persons])

    # normalize both data
    # respondents_df = normalize_persons(respondents_df)
    # persons_df = normalize_persons(persons_df)

    # compare dataframes
    # modified = identify_respondents(
    #    respondents=respondents_df, known_persons=persons_df
    # )
    # return modified

    # variant 1 use match_function
    # for item in respondents:
    #    resolved_df = match_persons(respondent=item, persons=persons_df)
    #    if(resolved_df is not None):
    #        for x in resolved_df:
    #            item.add_matching_id(x.uuid)
    #            count = count + 1

    output = []
    unmatched_tmp = []

    # variant 2 compare lists directly
    count = 0
    unm_cnt = 0
    for respondent in respondents:
        matching = False
        for person in persons:
            try:
                if (
                    respondent.given_name == person.given_name
                    and respondent.family_name == person.family_name
                    and respondent.affiliation == person.affiliation
                    and (len([x for x in respondent.labels if x in person.labels])) > 0
                ):
                    respondent.add_matching_id(person.openmedia_id)
                    output.append(respondent)
                    matching = True
                    count = count + 1
            except TypeError:
                print(f"There was an error importing contact: {count}")

        if not matching:
            unmatched_tmp.append(respondent)
            unm_cnt = unm_cnt + 1

    # remove duplicate entries
    unique_list = []
    unique_unmatched = []
    unique_all = []

    for x in output:
        if x not in unique_list:
            unique_list.append(x)
            unique_all.append(x)

    for x in unmatched_tmp:
        if x not in unique_unmatched:
            unique_unmatched.append(x)
            unique_all.append(x)

    print(f"Found: {count} matches and {unm_cnt} new ones.")

    # if none found try name only match
    # if count == 0:
    #    for respondent in respondents:
    #        for person in persons:
    #            if (
    #                respondent.given_name == person.given_name
    #                and respondent.family_name == person.family_name
    #            ):
    #                respondent.add_matching_id(person.openmedia_id)
    #                output.append(respondent)
    #                count = count + 1


    global unmatched
    unmatched = unique_unmatched

    global resolved
    resolved = unique_all

    global df_resolved
    df_resolved = list_to_dataframe(resolved)

    return unique_all


def persons_to_sqlite(input_persons: List[Person]) -> None:
    con = sqlite3.connect("tmp.sqlite")
    cur = con.cursor()
    cur.execute("DROP TABLE person;")
    cur.execute(
        "CREATE TABLE person ( openmedia_id,given_name,family_name,affiliation,gender,foreigner,labels);"
    )

    to_db = []
    for i in input_persons:
        to_db.append(
            [
                i.openmedia_id,
                i.given_name,
                i.family_name,
                i.affiliation,
                i.gender,
                i.foreigner,
                i.labels,
            ]
        )

    cur.executemany(
        "INSERT INTO person ( openmedia_id,given_name,family_name,affiliation,gender,foreigner,labels) VALUES (?, ?, ?, ?, ?, ?, ?);",
        to_db,
    )
    con.commit()
    con.close()


##############################################################################
# paste from cro-respodent-match
##############################################################################


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


    # Get only subset of columns.
    df = persons[
        [
            "unique_id",
            "given_name",
            "family_name",
            "affiliation",
            "gender",
            "labels",
            "foreigner",
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

    df.unique_id = df.unique_id.astype(str)
    df.unique_id = df.unique_id.str.strip()

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

    # 1. Transform respondent attributes for matching.

    respondent_given_name: str = respondent.given_name.strip().lower()
    respondent_family_name: str = respondent.family_name.strip().lower()
    respondent_affiliation: str = respondent.affiliation.strip().lower()
    respondent_labels: Set[str] = {x.strip().lower() for x in respondent.labels}

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
