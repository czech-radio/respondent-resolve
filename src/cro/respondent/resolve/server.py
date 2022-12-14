# -*- coding: utf-8 -*-
# from threading import Thread
import os


from flask import Flask, request, jsonify
from werkzeug.serving import WSGIRequestHandler
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
    return jsonify(
        [
            {"server": "cro-respondent-resolve"},
            {"version": "0.1.0"},
            {"persons": f"{len(persons)}"},
        ]
    )


@server.route("/uploader", methods=["POST", "GET"])
def upload_file():
    fn = request.args.get("file")  # .format()

    if request.method == "POST":
        f = request.files["file"]
        f.save(f"uploads/{fn}")

    global respondents
    respondents = load_respondents_from_file(fn)

    # seems to be unnecessary ?
    # global resolved
    # resolved = compare_respondents_to_persons(respondents=respondents, persons=persons)

    output = []
    for result in respondents:
        output.append(result.asdict())

    return jsonify(output)


@server.route("/respondents/<year>/<week>", methods=["GET"])
def get_respondents(year: int, week: int):

    global respondents
    respondents = load_respondents(year=year, week_number=week)

    output = []
    for respondent in respondents:
        output.append(respondent.asdict())

    return jsonify(output)


@server.route("/respondents", methods=["GET"])
def get_respondents_file():

    print(request.args.to_dict())
    fn = request.args.get("file")  # .format()

    global respondents
    respondents = load_respondents_from_file(fn)

    output = []
    for respondent in respondents:
        output.append(respondent.asdict())

    return jsonify(output)


@server.route("/persons", methods=["GET"])
def get_persons():

    output = []
    for person in persons:
        output.append(person.asdict())

    return jsonify(output)


@server.route("/persons/filter", methods=["GET"])
def get_person_tmp():

    print(request.args.to_dict())
    uuid = request.args.get("uuid")  # .format()
    family_name = request.args.get("family_name")  # .format()
    given_name = request.args.get("given_name")  # .format()

    print(family_name)

    persons_tmp = []

    if uuid is not None:
        persons_tmp = get_person_by_uuid(uuid=uuid.format(), input_persons=persons)
    elif given_name is not None and family_name is not None:
        persons_tmp = get_person_by_full_name(
            family_name=family_name,
            given_name=given_name.format(),
            input_persons=persons,
        )
    elif family_name is not None:
        persons_tmp = get_person_by_family_name(
            family_name.format(), input_persons=persons
        )
    else:
        ...

    if persons_tmp is None:
        ...

    output = []

    for person in persons_tmp:
        output.append(person.asdict())

    return jsonify(output)


@server.route("/resolved/<year>/<week>", methods=["GET"])
def resolved_year_week(year: int, week: int):


    # new thread
    # persons = load_persons(con)

    global respondents
    respondents = load_respondents(year=year, week_number=week)

    global resolved
    resolved = compare_respondents_to_persons(respondents=respondents, persons=persons)

    output = []
    for result in resolved:
        output.append(result.asdict())

    print(output)
    # result ok here

    return jsonify(output)


@server.route("/resolved", methods=["GET"])
def get_resolved():

    global resolved
    resolved = compare_respondents_to_persons(respondents=respondents, persons=persons)

    output = []
    for entry in resolved:
        output.append(entry.asdict())

    return jsonify(output)


def create_app() -> Flask:
    return server


def main():
    """
    The main application function.
    """

    global persons
    persons = load_saved_persons()

    server = create_app()

    # config Server app
    server.config["JSON_AS_ASCII"] = False
    server.config["JSON_SORT_KEYS"] = False
    server.config["UPLOAD_FOLDER"] = "uploads"
    WSGIRequestHandler.protocol_version = "HTTP/1.1"

    server.run(debug=True)
