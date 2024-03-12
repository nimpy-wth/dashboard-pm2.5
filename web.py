from dash import Dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output

import pandas as pd
import plotly.express as px
import datetime
from dateutil.relativedelta import relativedelta

data = pd.read_csv("cleaned_data.csv")
data["DATETIMEDATA"] = pd.to_datetime(data["DATETIMEDATA"], format="%Y-%m-%d %H:%M:%S")
data.sort_values("DATETIMEDATA", inplace=True)

predict_data = pd.read_csv("predict_data/merged_predict_data.csv")
predict_data["DATETIMEDATA"] = pd.to_datetime(predict_data["DATETIMEDATA"], format="%Y-%m-%d %H:%M:%S")
predict_data.sort_values("DATETIMEDATA", inplace=True)

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
        "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Air Quality Analytics: Understand Air Quality!"

navbar = html.Div(
    className="navbar",  # Added a class name for styling
    children=[
        html.Nav(
            className="nav",
            children=[
                html.A('Home', href='/'),
                html.A('Prediction', href='/prediction'),
            ]
        )
    ]
)

home_layout = html.Div(
    children=[
        navbar,
        html.Div(
            children=[
                html.P(children="🌞", className="header-emoji"),
                html.H1(
                    children="Air Quality Analytics", className="header-title"
                ),
                html.P(
                    children="Analyze the air quality data",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Parameter", className="menu-title"),
                        dcc.Dropdown(
                            id="parameter-filter",
                            options=[
                                {"label": param, "value": param}
                                for param in data.columns[1:]
                            ],
                            value="PM25",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range",
                            className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data["DATETIMEDATA"].min().date(),
                            max_date_allowed=data["DATETIMEDATA"].max().date(),
                            start_date=data["DATETIMEDATA"].min().date(),
                            end_date=data["DATETIMEDATA"].max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="line-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            className="menu-title"
                        ),
                        html.Div(
                            id="stats-table",
                            className="stats-table",
                        ),
                    ],
                    className="card",
                    style={"width": "48%", "float": "right"},  
                ),
                html.Div(
                    html.Div(
                    children=dcc.Graph(id="stats-chart", 
                    # style={"width": "48%", "float": "left"}
                    ),
                ),
                    className="card",
                    style={"width": "50%", "float": "left"}, 
                ),
            ],
            className="wrapper",
        ),
    ]
)

@app.callback(
    Output("line-chart", "figure"),
    [
        Input("parameter-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_chart(selected_parameter, start_date, end_date):
    mask = (
        (data["DATETIMEDATA"] >= start_date)
        & (data["DATETIMEDATA"] <= end_date)
    )
    filtered_data = data.loc[mask]
    trace = {
        "x": filtered_data["DATETIMEDATA"],
        "y": filtered_data[selected_parameter],
        "type": "lines",
        "name": selected_parameter,
    }
    layout = {
        "title": f"{selected_parameter} over Time",
        "xaxis": {"title": "Datetime"},
        "yaxis": {"title": selected_parameter},
        "colorway": ["#E26868"], 
    }
    return {"data": [trace], "layout": layout}


@app.callback(
    Output("stats-chart", "figure"),
    [
        Input("parameter-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_stats_chart(selected_parameter, start_date, end_date):
    
    mask = (
    (data["DATETIMEDATA"] >= start_date)
    & (data["DATETIMEDATA"] <= end_date)
)
    filtered_data = data.loc[mask]
    # static_values = {"Mean": 10, "Std": 2, "Min": 8, "Max": 15}  # Replace with actual calculations
    # stats = pd.DataFrame.from_dict({"Statistic": static_values.keys(), "Value": static_values.values()})
    stats = filtered_data[selected_parameter].describe().reset_index().round(2)
    stats.columns = ["Statistic", "Value"]

    fig = px.bar(
        stats,
        x="Statistic",
        y="Value",
        title=f"Statistics - {selected_parameter} ({start_date}-{end_date})",
        color="Statistic",
    ).update_layout(plot_bgcolor="#F5F5F5") 

    return fig


@app.callback(
    Output("stats-table", "children"),
    [
        Input("parameter-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_stats_table(selected_parameter, start_date, end_date):
    mask = (
        (data["DATETIMEDATA"] >= start_date)
        & (data["DATETIMEDATA"] <= end_date)
    )
    filtered_data = data.loc[mask]
    stats = filtered_data[selected_parameter].describe().reset_index().round(2)
    stats.columns = ["Statistic", "Value"]
    stats_table = dbc.Table.from_dataframe(stats, striped=True, bordered=True, hover=True, className="custom-table")
    
    title = html.Div(children=f"Statistics - {selected_parameter} ({start_date}-{end_date})", 
                    className="font-title")
    
    return [title, stats_table]

############################################# PREDICTION GRAPH #############################################

predict_page = html.Div(
    children=[
        navbar,
        html.Div(
            children=[
                html.P(children="🌞", className="header-emoji"),
                html.H1(
                    children="Air Quality Analytics", className="header-title"
                ),
                html.P(
                    children="Analyze the air quality data",
                    className="header-description",
                ),
            ],
            className="header",
        ),

        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Parameter", className="menu-title"),
                        dcc.Dropdown(
                            id="parameter-predict",
                            options=[
                                {"label": param, "value": param}
                                for param in predict_data.columns[1:]
                                # {"label": "PM25", "value": "PM25"},
                                # {"label": "O3", "value": "O3"},
                                # {"label": "WS", "value": "WS"},
                                # {"label": "WD", "value": "WD"},
                                # {"label": "TEMP", "value": "TEMP"},
                            ],
                            value="PM25",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range",
                            className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=predict_data["DATETIMEDATA"].min().date(),
                            max_date_allowed=predict_data["DATETIMEDATA"].max().date(),
                            start_date=predict_data["DATETIMEDATA"].min().date(),
                            end_date=predict_data["DATETIMEDATA"].max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="predict-chart", config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)

@app.callback(
    Output("predict-chart", "figure"),
    [
        Input("parameter-predict", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)

def update_predict_chart(selected_parameter, start_date, end_date):
    mask = (
        (predict_data["DATETIMEDATA"] >= start_date)
        & (predict_data["DATETIMEDATA"] <= end_date)
    )
    filtered_data = predict_data.loc[mask]
    trace = {
        "x": filtered_data["DATETIMEDATA"],
        "y": filtered_data[selected_parameter],
        "type": "lines",
        "name": selected_parameter,
    }
    layout = {
        "title": f"{selected_parameter} Prediction",
        "xaxis": {"title": "Datetime"},
        "yaxis": {"title": selected_parameter},
        "colorway": ["#579AF5"],  # or any other color
    }
    return {"data": [trace], "layout": layout}

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    dcc.Interval(id='interval-component',interval=60000)
    ]
)

@app.callback(Output('page-content', 'children'), 
            Input('url', 'pathname'),)

def display_page(pathname):
    if pathname == '/':
        return home_layout
    elif pathname == '/prediction':
        return predict_page
    else:
        return '404 Page Not Found'

if __name__ == "__main__":
    app.run_server(debug=True)