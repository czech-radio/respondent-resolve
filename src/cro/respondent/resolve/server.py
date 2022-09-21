# -*- coding: utf-8 -*-

import pandas as pd
import json
import os


from flask import Flask, request, jsonify
from werkzeug.serving import WSGIRequestHandler

from cro.respondent.resolve.domain import Respondent
from cro.respondent.resolve.service import *

# get host sysvars
AURA_TARGET_HOST = os.environ["AURA_TARGET_HOST"]
AURA_TARGET_PORT = os.environ["AURA_TARGET_PORT"]
AURA_TARGET_NAME = os.environ["AURA_TARGET_NAME"]
AURA_TARGET_USER = os.environ["AURA_TARGET_USER"]
AURA_TARGET_PASS = os.environ["AURA_TARGET_PASS"]


server = Flask(__name__)


@server.route("/", methods=["GET"])
def get_version():
    return jsonify([{"server": "cro-respondent-resolve"}, {"version": "0.1.0"}])


@server.route("/respondents/<year>/<week>", methods=["GET"])
def get_respondents(year: int, week: int):
    respondents = load_respondents(year=year, week_number=week)

    output = []
    for respondent in respondents:
        output.append(respondent.asdict())

    return jsonify(output)


@server.route("/persons", methods=["GET"])
def get_persons():
    con = create_connection_db(
        f"dbname={AURA_TARGET_NAME} user={AURA_TARGET_USER} host={AURA_TARGET_HOST} port={AURA_TARGET_PORT} password={AURA_TARGET_PASS}"
    )
    persons = load_persons(con)

    output = []
    for person in persons:
        output.append(person.asdict())

    return jsonify(output)


@server.route("/resolved/detail", methods=["GET"])
def get_person_tmp():
    if not persons:
        con = create_connection_db(
            f"dbname={AURA_TARGET_NAME} user={AURA_TARGET_USER} host={AURA_TARGET_HOST} port={AURA_TARGET_PORT} password={AURA_TARGET_PASS}"
        )
        persons = load_persons(con)

    uuid = f"{request.args.get('uuid')}"
    family_name = f"{request.args.get('family_name')}"
    given_name = f"{request.args.get('given_name')}"

    if uuid is not None:
        persons_tmp = get_person_by_uuid(uuid=uuid, input_persons=persons)
    elif given_name is not None and family_name is not None:
        persons_tmp = get_person_by_full_name(
            family_name=family_name, given_name=given_name, input_persons=persons
        )
    elif family_name is not None:
        persons_tmp = get_person_by_family_name(family_name, persons)
    else:
        ...
        # abort(500, "Necesarry arguments were not supplied")

    if persons_tmp is None:
        ...
        # abort(400, "Record were not found")

    output = []
    for person in persons_tmp:
        output.append(person.asdict())

    return jsonify(output)


@server.route("/resolved/<year>/<week>", methods=["GET"])
def resolved_year_week(year: int, week: int):

    if not persons:
        con = create_connection_db(
            f"dbname={AURA_TARGET_NAME} user={AURA_TARGET_USER} host={AURA_TARGET_HOST} port={AURA_TARGET_PORT} password={AURA_TARGET_PASS}"
        )
        persons = load_persons(con)

    if not repondents:
        respondents = load_respondents(year=year, week_number=week)

    results = compare_respondents_to_persons(respondents=_respondents, persons=_persons)

    output = []
    for result in results:
        output.append(result.asdict())

    print(output)
    # result ok here

    return jsonify(output)


@server.route("/resolved", methods=["GET"])
def resolved():
    return jsonify(
        compare_respondents_to_persons(respondents=respondents, persons=persons)
    )


def create_app() -> Flask:
    return server


def main():
    """
    The main application function.
    """
    server = create_app()

    # config Server app
    server.config["JSON_AS_ASCII"] = False
    server.config["JSON_SORT_KEYS"] = False
    WSGIRequestHandler.protocol_version = "HTTP/1.1"

    server.run(debug=True)
