import os
import time

from dash import Dash, dash_table, Input, Output, callback
import dash_bootstrap_components as dbc

import pandas as pd

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy


df = pd.read_json("http://localhost:5000/resolved/2022/36", orient="records")

print(df.head())

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        dbc.Label("Klikněte pro editaci."),
        dbc.Table.from_dataframe(df, striped=True, bordered=True, hover=True),
        dbc.Alert(id="tbl_out"),
    ]
)


@callback(Output("tbl_out", "children"), Input("tbl", "active_cell"))
def update_graphs(active_cell):
    return str(active_cell) if active_cell else "Click the table"


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=5001)
