import dash
import datetime
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import chart_studio.plotly as py
from plotly import graph_objs as go
import pandas as pd
import numpy as np
import os

df = pd.read_csv('data.csv',usecols= ['lat', 'lon','nomCapteur','etat','moyenne'])
newData = []
class PositionGeo:
    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

class PointParking:
    def __init__(self, lat, lon, nomCapteur, etat, moyenne):
        self.lat = lat
        self.lon = lon
        self.nomCapteur = nomCapteur
        self.etat = etat
        self.moyenne = moyenne

COLOR_REG_GOOD_V = '#03fc3d' # vert
COLOR_REG_GOOD = '#00FFFF' # bleu ciel
COLOR_REG_LIMIT = '#FFBF00' # yellow
COLOR_REG_BAD = '#FF0000' #red
COLOR_TRANSFO_HOVERLABEL = '#808080' #darkgrey
COLOR_TRANSFO_HOVERLABEL2 = '#4C4C4C' #grey nodata
COLOR_PHASE_A ='#007FFF'
COLOR_PHASE_B ='#FF6978'
COLOR_PHASE_C ='#420217'
COLOR_TEXTE = '#FFA630'
COLOR_BACKGROUND = '#383840'
external_stylesheets = ['https://codepen.io/pascal-chayer/pen/KKwGrYr.css']
linkDB = 'https://hackaton-32051.firebaseio.com/'
app = dash.Dash('TEAM 7 Hackatown2020',external_stylesheets=external_stylesheets)
mapbox_access_token = 'pk.eyJ1IjoibGFjOTAwIiwiYSI6ImNqcXF2b2lseTBnbW00M2xweDUyNmd4d3gifQ.3dM1QootSXt4NfSKMjFFqQ'
MapCenter = PositionGeo('45.535325', '-73.660670')
# CostcoParking1 = PointParking('45.535726', '-73.661380', 'Capteur1', True, '2:30')
# CostcoParking2 = PointParking('45.535873', '-73.661560', 'Capteur2', False, '1:50')
# CostcoParking3 = PointParking('45.535706', '-73.661112', 'Capteur3', False, '0:10')
# CostcoParking4 = PointParking('45.535605', '-73.661437', 'Capteur4', True, '5:30')

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Fetch the service account key JSON file contents
cred = credentials.Certificate(r'/Users/omidadibi/Downloads/hackaton-32051-firebase-adminsdk-9h2n3-881783b644.json')

# Initialize the app with a service account, granting admin privileges
firebase_admin.initialize_app(cred, {
    'databaseURL': linkDB
})

# # As an admin, the app has access to read and write all data, regradless of Security Rules
# ref = db.reference('capteur/1')
# data = ref.get()
# df = pd.DataFrame(data)
# print(len(data),df.iloc[0,-1])



def defineColor(bool):
    if bool:
        return COLOR_REG_BAD
    else:
        return COLOR_REG_GOOD_V

def createParkingPoint(pointP):

    point = go.Scattermapbox(
                lat=[pointP.lat],
                lon=[pointP.lon],
                mode='markers',
                marker=dict(
                    size = 14,
                    color = defineColor(pointP.etat),
                ),
                text= pointP.nomCapteur,
                name = "REGULATEUR",
                hoverinfo="text",
            )
    return point

def generatePoint(etatSensor):
    global df
    data = []
    for row in df.itertuples(index=False):
        # Convert named tuple to dictionary
        dictRow = row._asdict()
        point = PointParking(dictRow['lat'], dictRow['lon'], dictRow['nomCapteur'], dictRow['etat'], dictRow['moyenne'])
        data.append(createParkingPoint(point))
    point = PointParking('45.535573', '-73.660691', 'capteurReel', bool(etatSensor), '0:06')
    data.append(createParkingPoint(point))
    return data

mapLayout = go.Layout(
                margin= dict(
                        l=0,
                        r=0,
                        t=5,
                        b=10
                ),
                hovermode='closest',
                font=dict(
                    size = 18,
                    color = '#d8d8d8',
                    ),
                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    bearing=0,
                    center=dict(
                        lat=float(MapCenter.lat),
                        lon=float(MapCenter.lon)
                    ),
                    pitch=0,
                    zoom=17,
                    style="dark",

                ),
                autosize=True,
                paper_bgcolor = '#1E1E1E',
                height= 400,
                showlegend = False,
            )

graphLayout = go.Layout(
        bargap=0.01,
        bargroupgap=0,
        barmode="group",
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        showlegend=False,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        dragmode="select",
        font=dict(color="white"),
        xaxis=dict(
            range=[-0.5, 23.5],
            showgrid=False,
            nticks=25,
            fixedrange=True,
            ticksuffix=":00",
        ),
    )

## HTML
app.layout = html.Div([
    dcc.Interval(
            id='interval-component',
            interval=1*500, # in milliseconds
            n_intervals=0
        ),
    ## CODE DE MERDE
    html.Div([
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.Img(
                            className="logo", src="https://firebasestorage.googleapis.com/v0/b/hackaton-32051.appspot.com/o/Screen%20Shot%202020-06-29%20at%204.26.16%20PM.png?alt=media&token=8129e681-f3e1-460f-8af9-72a745b22102"
                        ),
                        html.H1(children = 'Parking traffic visualization'),
                        html.P(children = 'Here is an example of what our business web app would look like')
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    children=[
                        dcc.Graph(
                            id="map",
                            config={'displayModeBar':False},
                            figure={
                                    'data' : newData,
                                    'layout' : mapLayout
                                }
                            ),
                        dcc.Graph(
                            id="histogram",
                            figure={
                                    'data' : [{'x': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0], 'y': [10, 10, 10, 10, 10, 10, 30, 70, 100, 150, 100, 150, 200, 250, 300, 200, 100, 30, 10, 10, 10, 10, 10, 10], 'type': 'bar', 'name': 'SF'}],
                                    'layout' : graphLayout
                                }),
                    ],
                ),
            ],
        )
    ]
)
],
)

@app.callback(Output('map', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    global df
    global newData
    df = pd.read_csv('data.csv',usecols= ['lat', 'lon','nomCapteur','etat','moyenne'])
    ref = db.reference('capteur/1')
    data = ref.get()
    dbDF = pd.DataFrame(data)
    newData = generatePoint(dbDF.iloc[0,-1])


    return {'data' : newData,
                'layout': mapLayout }

if __name__ == '__main__':
    print(pd.Timestamp('now'))
    app.run_server(debug=True)