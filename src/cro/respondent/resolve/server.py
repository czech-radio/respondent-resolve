# -*- coding: utf-8 -*-

import pandas as pd

from flask import Flask, request, jsonify

from cro.respondent.resolve.domain import Respondent

respondents = {}

server = Flask(__name__)


@server.route("/", methods=["GET"])
def get_respondents():
    return jsonify([{}, {}])


def create_app() -> Flask:
    return server


def main():
    """
    The main application function.
    """
    server = create_app()
    server.run(debug=True)
