import io
import urllib.parse

import base64

import requests
from dash import Dash, dash_table, Input, Output, html, dcc
from dash.dependencies import Input, Output, State

import pandas as pd

df = pd.DataFrame()



print(df.columns)

app = Dash(__name__)

app.layout = html.Div(
    [
        dcc.Upload(
            id="upload-data",
            children=html.Div(
                ["drag and drop to import or click to ", html.A("select files")]
            ),
            style={
                "width": "50%",
                "height": "40px",
                "lineHeight": "40px",
                "borderWidth": "1px",
                "borderStyle": "dashed",
                "borderRadius": "5px",
                "textAlign": "center",
                "margin": "10px",
            },
            multiple=True,
        ),
        html.Div(id="output-data-upload"),
        html.Div(id="container"),
    ]
)


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(",")

    decoded = base64.b64decode(content_string)

    post_data = io.BytesIO(decoded)

    df_original = pd.DataFrame()

    try:
        if "xlsx" in filename.lower():
            # assume the file is zipped xls
            # df_original = pd.read_excel(
            #        io.BytesIO(decoded),
            #        sheet_name=0,
            #        header=None,
            #        engine="openpyxl"
            #        )

            print(f" loading {filename}")

            # POST data to server
            url = f"http://localhost:5000/uploader?file={filename}"
            files = {"file": post_data}
            response = requests.post(url, files=files, timeout=2400)
            df_original = pd.DataFrame.from_dict(response.json())
            print(df_original.head())
        else:
            return html.Div("File must be in xlsx format")

    except Exception as e:
        print(e)
        return html.Div(["There was an error processing this file."])

    cols = [col for col in df_original.columns if not (col.endswith("matching_ids"))]
    matching_ids = [";".join(i) for i in df_original["matching_ids"]]
    ids = list(range(0, len(df_original)))

    df = df_original[cols]

    df["id"] = ids
    df["matching_ids"] = matching_ids

    print("Data loaded Ok")

    return dash_table.DataTable(
        id="respondents-table",
        columns=[{"id": c, "name": c} for c in df.columns],
        hidden_columns=["id", "openmedia_id"],
        data=df.to_dict("records"),
        style_cell_conditional=[
            {"if": {"column_id": c}, "textAlign": "left"}
            for c in ["labels"]
            # for c in ["given_name", "family_name", "affiliation", "labels"]
        ],
        style_as_list_view=True,
        style_table={"overflowY": "scroll", "height": "400px"},
        style_cell={
            # "overflow": "hidden",
            # "textOverflow": "ellipsis",
            # "maxWidth": 100,
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
        selected_columns=[],
        selected_rows=[],
        page_action="native",
    )


@app.callback(
    Output("output-data-upload", "children"),
    Input("upload-data", "contents"),
    State("upload-data", "filename"),
    State("upload-data", "last_modified"),
)
def update_output(list_of_contents, list_of_names, list_of_dates):
    print(f"file(s) updated: {list_of_names}")
    children = []
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d)
            for c, n, d in zip(list_of_contents, list_of_names, list_of_dates)
        ]

    print(f"UPDATE invoked {list_of_dates}")

    # , [{"id": c, "name": c} for c in df.columns], df.to_dict("records")
    return children


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
    print(len(current["matching_ids"].split(";")))
    print(current["family_name"])

    # check if empty == 0
    if len(current["matching_ids"].split(";")) > 1:
        for matching_id in current["matching_ids"].split(";"):
            if matching_id:
                tmp = pd.read_json(
                    f"http://localhost:5000/persons/filter?uuid={matching_id}"
                )
                resolved = pd.concat([resolved, tmp], axis=0)
    else:
        family_name = urllib.parse.quote(current["family_name"], safe="")
        tmp = pd.read_json(
            f"http://localhost:5000/persons/filter?family_name={family_name}"
        )
        print(tmp)
        resolved = pd.concat([resolved, tmp], axis=0)

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


def main():
    app.run_server(host="0.0.0.0", debug=True, port=5001)
