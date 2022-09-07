# -*- coding: utf-8 -*-

import pandas as pd

from flask import Flask, request, jsonify

from cro.respondent.resolve.domain import Respondent
from cro.respondent.resolve.service import *

respondents = {}

server = Flask(__name__)


@server.route("/", methods=["GET"])
def get_version():
    return jsonify([{"server": "cro-respondent-resolve"}, {"version": "0.1.0"}])


@server.route("/get_respondents/<year>/<week>", methods=["GET"])
def get_respondents(year: int, week: int):
    return jsonify(load_respondents(year=year, week_number=week))


def create_app() -> Flask:
    return server


def main():
    """
    The main application function.
    """
    server = create_app()
    server.run(debug=True)
