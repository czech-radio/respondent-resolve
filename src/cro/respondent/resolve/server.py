# -*- coding: utf-8 -*-

import pandas as pd
import json

from flask import Flask, request, jsonify

from cro.respondent.resolve.domain import Respondent
from cro.respondent.resolve.service import *

respondents = []

server = Flask(__name__)


@server.route("/", methods=["GET"])
def get_version():
    return jsonify([{"server": "cro-respondent-resolve"}, {"version": "0.1.0"}])

@server.route("/respondents/<year>/<week>", methods=["GET"])
def get_respondents(year: int, week: int):
    respondents = load_respondents(year=year,week_number=week)

    output = []
    for respondent in respondents:
        output.append(respondent.asdict())

    return output

def create_app() -> Flask:
    return server


def main():
    """
    The main application function.
    """
    server = create_app()
    server.run(debug=True)
