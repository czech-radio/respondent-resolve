# -*- coding: utf-8 -*-

import pandas as pd
import json
import os


from flask import Flask, request, jsonify

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
    return load_persons(con)


def create_app() -> Flask:
    return server


def main():
    """
    The main application function.
    """
    server = create_app()
    server.run(debug=True)
