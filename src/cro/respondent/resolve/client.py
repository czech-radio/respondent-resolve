import os
import time
import urllib.parse

from dash import Dash, dash_table, Input, Output, callback, html
import dash_bootstrap_components as dbc

import pandas as pd

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy


df_original = pd.read_json("http://localhost:5000/resolved/2022/36", orient="records")
cols = [col for col in df_original.columns if not (col.endswith("matching_ids"))]
nmatch = [len(i) - 1 for i in df_original["matching_ids"]]
matching_ids = [";".join(i) for i in df_original["matching_ids"]]
ids = list(range(0, len(df_original)))
df = df_original[cols]

df["id"] = ids
#df["nmid"] = nmatch
df["matching_ids"] = matching_ids


# df = [['openmedia_id','given_name','family_name','affiliation','gender','foreigner','labels']]

print(df.columns)

app = Dash(__name__)

app.layout = html.Div(
    [
        dash_table.DataTable(
            id="respondents-table",
            data=df.to_dict("records"),
            columns=[{"id": c, "name": c} for c in df.columns],
            hidden_columns=["id","openmedia_id"],
            style_cell_conditional=[
                {"if": {"column_id": c}, "textAlign": "left"}
                for c in ["given_name", "family_name", "affiliation", "labels"]
            ],
            # style_data_coditional=[
            #     {"if": {'column_id': 'nmid', 'filter_query': '{' + field + '}' + ' < 1 '},
            #         'backgroundColor': '#ffcc00'
            #      } for field in df.columns
            #     ],
            style_as_list_view=True,
            style_cell={
                "overflow": "hidden",
                "textOverflow": "ellipsis",
                "maxWidth": 150,
                "padding": "5px",
            },
            style_header={
                "backgroundColor": "white",
                "fontWeight": "bold",
                "border": "1px solid black",
            },
            editable=True,
            sort_action="native",
            sort_mode="multi",
            row_selectable="multi",
            # row_deletable=True,
            selected_columns=[],
            selected_rows=[],
            page_action="native",
            page_current=0,
            page_size=15,
        ),
        html.Div(id="container"),
    ]
)


@app.callback(
    Output("container", "children"),
    Input("respondents-table", "derived_virtual_row_ids"),
    Input("respondents-table", "selected_row_ids"),
    Input("respondents-table", "active_cell"),
)
def update_graphs(row_ids, selected_row_ids, active_cell):

    selected_id_set = set(selected_row_ids or [])

    if row_ids is None:
        dff = df
        #    # pandas Series works enough like a list for this to be OK
        row_ids = df["id"]
    else:
        dff = df.loc[row_ids]

    active_row_id = active_cell["row_id"] if active_cell else 0

    current = df.loc[active_row_id]

    resolved = pd.DataFrame()
    print(len(current['matching_ids'].split(";")))
    print(current['family_name'])

    # check if empty == 0
    if len(current["matching_ids"].split(";")) > 1:
        for matching_id in current["matching_ids"].split(";"):
            if matching_id:
                tmp = pd.read_json(
                    f"http://localhost:5000/persons/filter?uuid={matching_id}"
                )
                resolved = pd.concat([resolved, tmp], axis=0)
    else:
        family_name = urllib.parse.quote(current["family_name"],safe="")
        tmp = pd.read_json(f"http://localhost:5000/persons/filter?family_name={family_name}")
        print(tmp)
        resolved = pd.concat([resolved,tmp],axis=0)

    if resolved.empty:
        return ["not found"]

    cols = [col for col in df_original.columns if not (col.endswith("matching_ids"))]
    resolved = resolved[cols]
    ids = list(range(0, len(resolved)))
    resolved["id"] = ids

    print(resolved)

    return html.Div(
        [
            dash_table.DataTable(
                id="matching-table",
                data=resolved.to_dict("records"),
                columns=[{"id": c, "name": c} for c in resolved.columns],
                hidden_columns=["openmedia_id", "matching_ids", "id"],
                style_cell_conditional=[
                    {"if": {"column_id": c}, "textAlign": "left"}
                    for c in ["given_name", "family_name", "affiliation", "labels"]
                ],
                style_as_list_view=True,
                style_cell={"padding": "5px"},
                style_header={
                    "backgroundColor": "#ffcc00",
                    "fontWeight": "bold",
                    "border": "1px solid black",
                },
                editable=True,
                sort_action="native",
                sort_mode="multi",
                column_selectable="single",
                row_selectable="single",
                page_action="native",
                page_current=0,
                page_size=10,
            )
        ]
    )


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True, port=5001)
