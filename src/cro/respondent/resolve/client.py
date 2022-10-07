import os
import time

from dash import Dash, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc

import pandas as pd

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy


df_original = pd.read_json("http://localhost:5000/resolved/2022/36", orient="records")
cols = [
    col
    for col in df_original.columns
    if not (col.endswith("matching_ids") or col.endswith("openmedia_id"))
]
df = df_original[cols]

# df = [['openmedia_id','given_name','family_name','affiliation','gender','foreigner','labels']]

print(df.head())
print(df.columns)

app = Dash(__name__)

# app.layout = dbc.Container(
#    [
#        dbc.Label("Klikněte pro editaci."),
#        dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True),
#        dbc.Alert(id="tbl_out"),
#    ]
# )

app.layout = dash_table.DataTable(
    data=df.to_dict("records"),
    columns=[{"id": c, "name": c} for c in df.columns],
    style_cell_conditional=[
        {"if": {"column_id": c}, "textAlign": "left"}
        for c in ["given_name", "family_name", "affiliation", "labels"]
    ],
    style_as_list_view=True,
    style_cell={"padding": "5px"},
    style_header={
        "backgroundColor": "white",
        "fontWeight": "bold",
        "border": "1px solid black",
    },
    editable=True,
)


# @callback(Output("tbl_out", "children"), Input("tbl", "active_cell"))
# def update_graphs(active_cell):
#    return str(active_cell) if active_cell else "Click the table"


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=5001)
