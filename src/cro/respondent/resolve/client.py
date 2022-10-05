import os
import time

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tmp.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Person(db.Model):
    openmedia_id = db.Column(db.String(64), primary_key=True)
    given_name = db.Column(db.String(64), index=True)
    family_name = db.Column(db.String(64), index=True)
    affiliation = db.Column(db.String(64), index=True)
    gender = db.Column(db.Integer, index=True)
    foreigner = db.Column(db.Integer, index=True)
    labels = db.Column(db.String(256))

    def to_dict(self):
        return {
            "openmedia_id": self.openmedia_id,
            "given_name": self.given_name,
            "family_name": self.family_name,
            "affiliation": self.affiliation,
            "gender": self.gender,
            "foreigner": self.foreigner,
            "labels": self.labels,
        }


db.create_all()


@app.route("/files")
def files():
    path = "/mnt/R/GŘ/Strategický rozvoj/Kancelář/Analytics/Source/2022/batch_krystof"
    dir_list = os.listdir(path)
    return render_template("files_select.html", data=dir_list)


@app.route("/")
def index():
    return render_template("persons_table.html", title="CRO respondents resolver")


@app.route("/api/data")
def data():
    query = Person.query

    # search filter
    search = request.args.get("search[value]")
    if search:
        query = query.filter(
            db.or_(
                Person.given_name.like(f"%{search}%"),
                Person.family_name.like(f"%{search}%"),
            )
        )
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f"order[{i}][column]")
        if col_index is None:
            break
        col_name = request.args.get(f"columns[{col_index}][data]")
        if col_name not in ["openmedia_id", "given_name", "family_name", "affiliation"]:
            col_name = "family_name"
        descending = request.args.get(f"order[{i}][dir]") == "desc"
        col = getattr(Person, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get("start", type=int)
    length = request.args.get("length", type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        "data": [person.to_dict() for person in query],
        "recordsFiltered": total_filtered,
        "recordsTotal": Person.query.count(),
        "draw": request.args.get("draw", type=int),
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
