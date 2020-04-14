#%%List of import
import os 
import plotly.graph_objs as go
import dash
import dash_table as dasht
import dash_core_components as dcc
import dash_html_components as html
import dash_daq as daq
from dash.dependencies import Input, Output, State
from pathlib import Path
###from dashserver import server
import pandas as pd
import numpy as np

#%%Global Variable

hertzP = Path(r"//Rpisln800-sf/donnees_hertz/USAGERS/CW8912/data/apps/gdihdf/")
DBcomment = r'//Rpisln800-sf/donnees_hertz/USAGERS/CW8912/data/apps/regulateurs/CommentDB.hdf'
LinkInfo = 'http://pv400436.bur.hydro.qc.ca/RegInfo.html'

COLOR_REG_GOOD_V = '#ADFF2F' # vert
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

VOLT_SETPOINT = 122.5
ECART_SETPOINT = 3
BANDE_MORTE = 1
CODE_JOUR = 0
CODE_TEMPS = -1
ecart = ((VOLT_SETPOINT/100)*ECART_SETPOINT)
BORNE_MIN = VOLT_SETPOINT - ecart
BORNE_MAX = VOLT_SETPOINT + ecart

allday = []
droplabelDay = []
newData=[]

userConnect=''
buttonClick = 0
buttonClickReset = None
buttonClickDelete = 0
CED = None

#%%MapBox Token
mapbox_access_token = 'pk.eyJ1IjoibGFjOTAwIiwiYSI6ImNqcXF2dWhmNDBmZmgzeGxjcGpxczVzdm0ifQ.jK1cnKIJ8a9oQHngr2_QZA'

#%% Format Data
def getData(day,time):
    columnsNeeded = ['CED_LCLCL', 'DISTANCE_KM', 'TYPE_APPAREIL', 'LONGITUDE', 'LATITUDE',
       'PHASE', 'CAPACITE_KVA', 'POSITION', 'REG_RELATE', 'SIGLE_POSTE_NO',
       'V_PHASE_A', 'V_PHASE_B', 'V_PHASE_C']
    if time == -1:
        keys = pd.read_feather(r'{0}/{1}/15m/regu.feather'.format(hertzP,day),columns=columnsNeeded)
        return keys
    else:
        columnsNeeded_Time = ['CED_LCLCL', 'DISTANCE_KM', 'TYPE_APPAREIL', 'LONGITUDE', 'LATITUDE',
           'PHASE', 'CAPACITE_KVA', 'POSITION', 'REG_RELATE', 'SIGLE_POSTE_NO',
           'V_PHASE_A_{0}'.format(time), 'V_PHASE_B_{0}'.format(time), 'V_PHASE_C_{0}'.format(time)]
        keys = pd.read_feather(r'{0}/{1}/15m/regu.feather'.format(hertzP,day),columns=columnsNeeded_Time)
        keys.columns = columnsNeeded
        return keys

#%%Map Layout

mapLayout= go.Layout(
                margin= dict(
                        l=0,
                        r=0,
                        t=40,
                        b=10
                ),
                hovermode='closest',
                title='Chargement',
                font=dict(
                    color=COLOR_TEXTE,
                    size = 18,
                    ),
                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    bearing=0,
                    center=dict(
                        lat=46,
                        lon=-74
                    ),
                    pitch=0,
                    zoom=7
                ),
                autosize=True,
                height= 600,
                paper_bgcolor = COLOR_BACKGROUND,
                showlegend = False,
            )
                         
#%% Graph Data

graphData = []
            
graphlayout = go.Layout(
            font=dict(
                    color=COLOR_TEXTE,
                    size = 18,
                    ),
            title='Graphique Régulateur',
            showlegend = False,
            margin=go.layout.Margin(l=40, r=0, t=40, b=30),
            paper_bgcolor = COLOR_BACKGROUND,
            height = 300,
            hovermode=False,
            hoverdistance = 0,
            )
            
graphlayout2 = go.Layout(
            font=dict(
                    color=COLOR_TEXTE,
                    size = 18,
                    ),
            title='Graphique Compteur',
            showlegend = False,
            margin=go.layout.Margin(l=40, r=0, t=40, b=30),
            paper_bgcolor = COLOR_BACKGROUND,
            height = 300,
            hovermode='closest'
            )

#%%Data Recovery
            
allData = []    
allDatacol = [] 
allregData = []
allregDatacol = []
allregDataR = []
allTransfoData = []
transfoGroup = []
alldataUse = []
dataUse = []

def dataread(code,temps): 
    global allData
    global allDatacol
    global allregData
    global allregDatacol
    global allregDataR
    global allTransfoData
    global transfoGroup
    global alldataUse
    global dataUse
    try:
        allData = getData(code,temps)
    except:
        print('Cant Read The Data')
        return
    
    allDatacol = [{"name": i, "id":i } for i in allData.columns]
    allDatacol.remove({'id': 'LONGITUDE', 'name': 'LONGITUDE'})
    allDatacol.remove({'id': 'LATITUDE', 'name': 'LATITUDE'})
    allDatacol.remove({'id': 'POSITION', 'name': 'POSITION'})
    allDatacol.remove({'id': 'DISTANCE_KM', 'name': 'DISTANCE_KM'})
    
    allregData = allData[(allData['TYPE_APPAREIL'] == 'RR' ) | (allData.TYPE_APPAREIL == 'RG' )]
    allregData = allregData.drop(columns=['REG_RELATE','POSITION','V_PHASE_A','V_PHASE_B','V_PHASE_C'])
    allregData['STATUS'] = 0
    allregDatacol = [{"name": i, "id":i } for i in allregData.columns]
    allregDataR = allregData.to_dict('rows')
    allregDatacol.remove({'id': 'LONGITUDE', 'name': 'LONGITUDE'})
    allregDatacol.remove({'id': 'LATITUDE', 'name': 'LATITUDE'})
    
    allTransfoData = allData[(allData.TYPE_APPAREIL != 'RR' ) & (allData.TYPE_APPAREIL != 'RG' )]
    transfoGroup = allTransfoData.groupby(['REG_RELATE','POSITION'])
    
    alldataUse = allTransfoData.to_dict("rows")
    dataUse = alldataUse

def get_allday():
    global allday
    global droplabelDay
    allday = [x.name for x in hertzP.glob('*') if x.is_dir()]
    alldayFor = [x.name for x in hertzP.glob('*') if x.is_dir()]
    droplabelDay = []
    for day in alldayFor:
        do = True
        for directory in os.listdir('{0}/{1}'.format(hertzP,day)):
             if directory == 'csv':
                do = False
                allday.pop(allday.index(day))
        if do:
            temp = dict(
                    label = day,
                    value = day
                    )
            droplabelDay.append(temp)
        
get_allday()

heure = 0
minute = 0
alllist = []
for i in range(97):
    if i%4 ==0 and i != 0:
        heure = heure + 1
        minute = 0
        alllist.append("{0}H {1}min".format(heure,minute))
    else:
        if i != 0:
            minute = minute + 15
        alllist.append("{0}H {1}min".format(heure,minute))

dropLabelTime = []
for i in range(96):
    temp = dict(
            label = '{0} a {1}'.format(alllist[i],alllist[i+1]),
            value = i
            )
    dropLabelTime.append(temp)
dropLabelTime.append({'label': 'Toute La Journée', 'value': -1})

dataread(allday[-1],-1)




colComt = ['Auteur','Date Du Commentaire','Parametre','Commentaire','Categorie','REGULATEUR']
colCom = [{"name": i, "id":i } for i in colComt]
regComment = pd.read_hdf(DBcomment)
sortArray= ['Date Du Commentaire','Categorie','Commentaire']
regComment.sort_values(by=sortArray,ascending=False,inplace=True)
regCommentData = regComment.to_dict("rows")
#%%External Css laditude 
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

#%%Generate the app
###app = dash.Dash(name='app', sharing=True, server=server, url_base_pathname='/regu/',external_stylesheets=external_stylesheets)
###app.config.update({'routes_pathname_prefix': '','requests_pathname_prefix': ''})
###app.css.append_css({'external_url': 'http://pv400436.bur.hydro.qc.ca/assets/style.css'}) 
app = dash.Dash(__name__, external_stylesheets=external_stylesheets ,url_base_pathname='/regulateur/')
# app.css.append_css({'external_url': 'https://codepen.io/pascal-chayer/pen/qveoaV.css'}) 
server = app.server
app.config.suppress_callback_exceptions = True
#%%Change tabs name
app.title = 'OR (Beta V2)'

#%%Begin of the html tree 
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

connectLayout = html.Div([
                html.Div([
                    html.Label("Nom d'utilisateur", className="label",id='F'),
                    dcc.Input(id='User', type='text', value=userConnect),
                    html.Button('Entrer',id='enter',accessKey="S")
                ],id='Name_Login'),
        ],className='TitreTab')
        
MDPconnectLayout = html.Div([
        html.Div([
                html.Label("Mot de Passe", className="label",id='F'),
                dcc.Input(id='User', type='password', value=''),
                html.Button('Entrer',id='enter',accessKey="S")]
            ,id='Name_Login'),
        ],className='TitreTab')
        
appLayout = html.Div([
        
    html.H1('OR', id='titre',),
    html.Div([
            daq.Indicator(
                className='Code',
                color=COLOR_TRANSFO_HOVERLABEL2,
                label="CODE 0: Données manquantes",
                style={'margin-right': 50},
                value=True
                ),
            daq.Indicator(
                className='Code',
                color=COLOR_REG_GOOD,
                label="CODE 1: Régulateur Correct",
                style={'margin-right': 50},
                value=True
                ),
            daq.Indicator(
                className='Code',
                color=COLOR_REG_LIMIT,
                label="CODE 2: En dehors du pourcentage d'écart, mais de moins de 1V",
                style={'margin-right': 50},
                value=True
                ),
            daq.Indicator(
                className='Code',
                color=COLOR_REG_BAD,
                label="CODE 3: En dehors de la plage spécifiée",
                value=True
                ),
            ],className='idTest'),
    html.Div([
    html.Div([
    html.Br(),
        #Map
        html.Div([
            html.Div([
                    dcc.Graph(
                       id="map",
                       config={'displayModeBar':False},
                       figure={
                               'data' : newData,
                               'layout' : mapLayout
                            }
                       ),
               ],className='insideRowMap'),
            html.Div([
                    dcc.Graph(
                        figure=go.Figure(
                            data=graphData,
                            layout=graphlayout
                            ),
                        id='V_Graph',
                        className= 'Graph',
                        config={'displayModeBar':False},
                        ),
                    dcc.Graph(
                        figure=go.Figure(
                            data=graphData,
                            layout=graphlayout2
                            ),
                        id='V_Graph_Compteur',
                        className= 'Graph',
                        config={'displayModeBar':False},
                        ),
                    ],className='insideRowMap')

            ],className='rowMap'),
    
    ],className='ContentColumns'),
                        
                        
            
    html.Div([
            html.Div([
                html.Label("Pourcentage d'écart V", className="label"),
                dcc.Input(id='pourcentage', type='number', value=ECART_SETPOINT,step=0.5)]),
            html.Div([
                    html.Label("Valeur de Comparaison", className="label"),
                    dcc.Input(id='comparaison', type='number', value=VOLT_SETPOINT,step=0.5)]),
            html.Div([
                    html.Label("CED", className="label"),
                    dcc.Dropdown(
                        id='ced',
                        options=[
                            {'label': 'IDM', 'value': 'IDM'},
                            {'label': 'LAV', 'value': 'LAV'},
                            {'label': 'MAT', 'value': 'MAT'},
                            {'label': 'ORL', 'value': 'ORL'},
                            {'label': 'SEI', 'value': 'SEI'},
                        ],
                        value=None
                    ),
                    ]),
            html.Div([
                    html.Label("LCLCL Du Régulateur", className="label"),
                    dcc.Input(id='lclcl', type='text', value="")]),
            html.Div([
                    html.Label("Code", className="label"),
                    dcc.Dropdown(
                        id='code',
                        options=[
                            {'label': '1', 'value': '1'},
                            {'label': '2', 'value': '2'},
                            {'label': '3', 'value': '3'},
                            {'label': '0', 'value': '0'},
                        ],
                        value=''
                    ),
                    ]),
                            
             html.Div([
                html.Label("Jour", className="label"),
                dcc.Dropdown(
                    id='jour',
                    options=droplabelDay,
                    value=allday[-1]
                ),
                ]),
            html.Div([
                html.Label("Temps", className="label"),
                dcc.Dropdown(
                    id='temps',
                    options=dropLabelTime,
                    value=-1
                ),
                ]),        
            
            html.Div([
                    html.Label("Catégorie", className="label"),
                    dcc.Dropdown(
                        id='FiltreCat',
                        options=[
                                {'label': 'Aucune/Autre Catégorie', 'value': 0},
                                {'label': 'Inspection requise par technicien', 'value': 1},
                                {'label': 'Restriction apposée', 'value': 2},
                                {'label': 'Régulateur contourne', 'value': 3},
                                {'label': 'Mise en route non complèté', 'value': 4},
                                {'label': 'Démentelement', 'value': 5},
                            ],
                        value=''
                    ),
                    ]),
           
            html.Div([
                        html.Label("Afficher les Transformateurs", className="label"),
                        daq.ToggleSwitch(
                            id='toggleTransfo',
                            value=False,
                            label=['OFF','ON'],
                            color='black'
                        ),       
                        ]),
            html.Div([
                    html.Label("Afficher en KM", className="label"),
                    daq.ToggleSwitch(
                        id='toggleKM',
                        value=True,
                        label=['OFF','ON'],
                        color='black'
                    ),       
                    ],),
            
            ],className='OptionsColumns'),
], className='BigContainer'),                 
                        
                        
                        
                        
                        
    html.Br(),
        
    html.Details([
        html.Summary('Note des régulateurs'),            
        html.Div([
                html.Label("Note sur régulateur", className="TitreTab"),
                dasht.DataTable(id="tabNoteReg",
                                data = regCommentData,
                                sorting=True,
                                row_selectable="single",
                                columns=colCom,
                                style_as_list_view = False,
                                style_table={
                                     'maxHeight': '320'},
                                style_cell={
                                        'minWidth': '0px','text-align':'center','color':'black'
                                        },
                                style_cell_conditional=[
                                        {'if': {'column_id': 'REGULATEUR'},
                                         'display': 'auto'},
                                        {'if': {'column_id': 'Parametre'},
                                         'width': '20%'},
                                        {'if': {'column_id': 'Date Du Commentaire'},
                                         'width': '5%'},
                                        {'if': {'column_id': 'Auteur'},
                                         'width': '7%'},
                                    ],
                                pagination_settings={
                                        'current_page': 0,
                                        'page_size': 9,
                                        },
                                ),
                html.Button('Effacer',id='Delete'),
                html.Div([
                         html.Div([
                                html.Label("Catégorie", className="label"),
                                dcc.Dropdown(
                                    id='Type',
                                    options=[
                                        {'label': 'Aucune/Autre Catégorie', 'value': 0},
                                        {'label': 'Inspection requise par technicien', 'value': 1},
                                        {'label': 'Restriction apposée', 'value': 2},
                                        {'label': 'Régulateur contourne', 'value': 3},
                                        {'label': 'Mise en route non complèté', 'value': 4},
                                        {'label': 'Démentelement', 'value': 5},
                                    ],
                                    value=0
                                ),
                                ]),
                         dcc.Textarea(
                                 id='Commentaire',
                                 placeholder='Entrer votre commentaire',
                                 draggable = False),
                        
                         html.Button('Valider',id='EntrerCom'),
                         html.Button('Réinitialiser les Régulateurs',id='resetReg'),
                                 ],id='Comment',className='RowCom'),
                ]),
            ],className='DropDetails'),
        
    html.Details([
        html.Summary('Tableau Transformateur'),            
        html.Div([
                html.Label("Tableau des Transformateurs", className="TitreTab"),
                dasht.DataTable(id="tabTransfo",
                                data = dataUse,
                                columns=allDatacol,
                                style_as_list_view = True,
                                style_table={
                                     'maxHeight': '320'},
                                style_cell={
                                        'minWidth': '140px', 'width': '140px', 'maxWidth': '140px',
                                        },
                                pagination_settings={
                                        'current_page': 0,
                                        'page_size': 9,
                                        },
                                )
                ]),
            ],className='DropDetails'),

    
    html.Details([
        html.Summary('Tableau Régulateur'), 
        html.Div([
                html.Label("Tableau des Régulateurs", className="TitreTab"),
                dasht.DataTable(id="tabReg",
                                data = allregDataR,
                                columns=allregDatacol,
                                style_as_list_view = True,
                                style_table={
                                     'maxHeight': '320'},
                                style_cell={
                                        'minWidth': '140px', 'width': '140px', 'maxWidth': '140px',
                                        },
                                pagination_settings={
                                        'current_page': 0,
                                        'page_size': 9,
                                        },
                                )
                ]),
            ],className='DropDetails'),
   
                
          
html.Footer(["2019 Développé par des stagiaires en Génie Logiciel :", html.A('Omid Adibi', href='http://omidadibi.com/',target="_blank"), " et Pascal Chayer sous la supervision de Laurier Demers", html.A('DOC', href=LinkInfo,target="_blank")]),
    html.Div(id='TransfoHidMap',style={'display':'none'}),
    html.Div(id='TransfoHidTab',style={'display':'none'}),
    html.Div(id='RegSelec', style={'display':'none'}),
    html.Div(userConnect,id='User', style={'display':'none'})
],className='AllPage')#End of page

testLayout = html.Div([html.Div(connectLayout)],id='waw')

#%%Fonction
def chooseRegColor(tabinfo):
    tabcolor = []
    for info in tabinfo:
        if info%10==0:
            tabcolor.append(COLOR_TRANSFO_HOVERLABEL2)
        if info%10==1:
            tabcolor.append(COLOR_REG_GOOD)
        if info%10==2:
            tabcolor.append(COLOR_REG_LIMIT)
        if info%10==3:
            tabcolor.append(COLOR_REG_BAD)
    return tabcolor

def chooseRegColorContour(tabinfo):
    tabcolor = []
    for info in tabinfo:
        if info < 20 and info >= 10:
            tabcolor.append(COLOR_REG_GOOD)
        if info < 10 and info >= 0:
            tabcolor.append(COLOR_TRANSFO_HOVERLABEL2)
        if info < 30 and info >= 20:
            tabcolor.append(COLOR_REG_LIMIT)
        if info < 40 and info >= 30:
            tabcolor.append(COLOR_REG_BAD)
    return tabcolor

def createREGPoint(lat,lon,info,condit):

    point = go.Scattermapbox(
                lat=lat,
                lon=lon,
                mode='markers',
                marker=dict(
                    size = 10,
                    color = chooseRegColor(condit),
                ),
                text=info,
                name = "REGULATEUR",
                hoverinfo="text",
            )
    return point

def createREGPoint2(lat,lon,info,condit):

    point = go.Scattermapbox(
                lat=lat,
                lon=lon,
                mode='markers',
                marker=dict(
                    size = 14,
                    color = chooseRegColorContour(condit),
                ),
                text=info,
                name = "REGULATEUR",
                hoverinfo="text",
            )
    return point

def chooseBgColor(tabinfo):
    tabcolor = []
    for info in tabinfo:
        if info=='Avant':
            tabcolor.append(COLOR_TRANSFO_HOVERLABEL)
        else:
            tabcolor.append(COLOR_TRANSFO_HOVERLABEL2)
    return tabcolor

def createTransfoPoint(lat,lon,info,condit):
    
    point = go.Scattermapbox(
                lat=lat,
                lon=lon,
                mode='markers',
                marker=dict(
                    symbol = 'star',
                    color = COLOR_TRANSFO_HOVERLABEL,
                    size = 10,
                ),
                hoverlabel=dict(
                    bgcolor=chooseBgColor(condit)
                ),
                text=info,
                name = "TRANSFO",
                hoverinfo="text",
            )
    return point

def selectData(tabdataUse,tabReg,transfo):
    transtablat = []
    transtablon = []
    transtabInfo = []
    transCondit = []
    reglat = []
    reglon = []
    regInfo = []
    regCondit = []
    newdf = pd.DataFrame(tabdataUse)

    for i in range(len(newdf)):
        if newdf.at[i,"V_PHASE_A"] == None:
            newdf.at[i,"V_PHASE_A"] = np.float64(np.nan)
        if newdf.at[i,"V_PHASE_B"] == None:
            newdf.at[i,"V_PHASE_B"] = np.float64(np.nan)
        if newdf.at[i,"V_PHASE_C"] == None:
            newdf.at[i,"V_PHASE_C"] = np.float64(np.nan)
        transtablat.append(newdf.at[i,"LATITUDE"])
        transtablon.append(newdf.at[i,"LONGITUDE"])
        
        infoString = "CED_LCLCL: {0}<br>Type d'appareil: {1}<br>Phase: {2}<br>Régulateur relié: {3}<br>V_PHASE A: {4}<br>V_PHASE B: {5}<br>V_PHASE C: {6}<br>KVA: {7}".format(
                newdf.at[i,"CED_LCLCL"],
                newdf.at[i,"TYPE_APPAREIL"],
                newdf.at[i,"PHASE"],
                newdf.at[i,"REG_RELATE"],
                newdf.at[i,"V_PHASE_A"].round(5),
                newdf.at[i,"V_PHASE_B"].round(5),
                newdf.at[i,"V_PHASE_C"].round(5),
                newdf.at[i,'CAPACITE_KVA'])
        transtabInfo.append(infoString)
        transCondit.append(newdf.at[i,"POSITION"])
    newregdata = pd.DataFrame(tabReg)
    regComment = pd.read_hdf(DBcomment)
    for i in range(len(newregdata)):
        data = regComment[regComment['REGULATEUR'] == newregdata.iloc[i].CED_LCLCL]
        data = data.sort_values(by=sortArray,ascending=False)
        try:
            recent = data.iloc[0]
        except:
            recent = pd.DataFrame(data=np.array([["","","","Aucun commentaire sur ce Régulateur","None",""]]),columns = colComt).iloc[0]
            
        reglat.append(newregdata.iloc[i].LATITUDE)
        reglon.append(newregdata.iloc[i].LONGITUDE)
        infoString = "CED_LCLCL: {0}<br>Type d'appareil: {1}<br>Phase: {2}<br>Ligne: {3}<br>KVA: {4}<br>Status: {5}<br>Dernier Commentaire: {6}".format(
                newregdata.iloc[i].CED_LCLCL,
                newregdata.iloc[i].TYPE_APPAREIL,
                newregdata.iloc[i].PHASE,
                newregdata.iloc[i].SIGLE_POSTE_NO,
                newregdata.iloc[i].CAPACITE_KVA,
                recent.Categorie,
                recent.Commentaire)
        regInfo.append(infoString)
        regCondit.append(newregdata.iloc[i].STATUS)
    newData = []
    newData.append(createREGPoint2(reglat,reglon,regInfo,regCondit))
    newData.append(createREGPoint(reglat,reglon,regInfo,regCondit))
    newData.append(createTransfoPoint(transtablat,transtablon,transtabInfo,transCondit))
    if transfo != None:
        lat = newdf[newdf.CED_LCLCL == transfo].LATITUDE
        lon = newdf[newdf.CED_LCLCL == transfo].LONGITUDE
        point = go.Scattermapbox(
                lat=lat,
                lon=lon,
                mode='markers',
                marker=dict(
                    symbol = 'circle-stroked',
                    color = COLOR_REG_GOOD_V,
                    size = 10,
                ),
                name = "Select",
                hoverinfo="skip",
            )
        newData.append(point)
    return newData

def OutOfRange(value,bandeMorte = False):
    if bandeMorte:
        return value <= BORNE_MIN - BANDE_MORTE or value >= BORNE_MAX + BANDE_MORTE
    else:
        return value <= BORNE_MIN or value >= BORNE_MAX

def StatusAvant(mean):
    
    if mean != mean:
        return 0
    elif OutOfRange(mean,True):
        return 30
    elif OutOfRange(mean):
        return 20
    else:
        return 10

def StatusApres(mean):
    
    if mean != mean:
        return 0
    elif OutOfRange(mean,True):
        return 3
    elif OutOfRange(mean):
        return 2
    else:
        return 1    
      
def getStatus(meanApres,meanAvant):
    value = StatusApres(meanApres) + StatusAvant(meanAvant)
    return value

def checkReg(regData):
    col = ['CED_LCLCL', 'DISTANCE_KM', 'TYPE_APPAREIL', 'LONGITUDE', 'LATITUDE',
       'PHASE', 'CAPACITE_KVA', 'POSITION', 'REG_RELATE', 'SIGLE_POSTE_NO',
       'V_PHASE_A', 'V_PHASE_B', 'V_PHASE_C']
    try:
        transfoAvant = transfoGroup.get_group((regData.CED_LCLCL,'Avant'))
    except:
        transfoAvant = pd.DataFrame(columns=col)
                    
    try:
        transfoApres = transfoGroup.get_group((regData.CED_LCLCL,'Apres'))
    except:
        transfoApres = pd.DataFrame(columns=col)
    regPHASE = regData.PHASE
    status =[]
    if 'A' in regPHASE:
        meanAvant = transfoAvant.V_PHASE_A.mean()
        meanApres = transfoApres.V_PHASE_A.mean()
        status.append(getStatus(meanApres,meanAvant))
        
    if 'B' in regPHASE:
        meanAvant = transfoAvant.V_PHASE_B.mean()
        meanApres = transfoApres.V_PHASE_B.mean()
        status.append(getStatus(meanApres,meanAvant))
    if 'C' in regPHASE:
        meanAvant = transfoAvant.V_PHASE_C.mean()
        meanApres = transfoApres.V_PHASE_C.mean()
        status.append(getStatus(meanApres,meanAvant))
        
    regData.at['STATUS'] = max(status)
    return regData

def RecalculateStatus():
    global allregData
    allregData = allregData.apply(checkReg,axis=1)  

# DOIT ETRE EXECUTER UNE FOIS AU DEPART_____________________________
RecalculateStatus()
allregData.sort_values(by='STATUS',ascending=False,inplace=True)
allregDataR = allregData.to_dict('rows')
##__________________________________________________________________

def genererRegGraphFig(ced_lclcl, transfoCED,km):
    regDataTransfo = allData[allData.REG_RELATE == ced_lclcl]
    regIndex = regDataTransfo[regDataTransfo.CED_LCLCL == ced_lclcl].index[0]
    if km:
        xRange = regDataTransfo['DISTANCE_KM']
        regX = 0
        xRange.pop(regIndex)
        textX='Distance (km)'
    else:
        xRange = list(range(len(regDataTransfo)))
        regX = regIndex - regDataTransfo.first_valid_index()
        xRange.pop(regX) 
        textX='Numéro de position'
    phase = regDataTransfo.loc[regIndex].PHASE
    try:
        minT = (min(min(regDataTransfo['V_PHASE_B'].dropna().get_values()),min(regDataTransfo['V_PHASE_A'].dropna().get_values()),min(regDataTransfo['V_PHASE_C'].dropna().get_values()),BORNE_MIN))
    except:
        minT = BORNE_MIN
    try:
        maxT = (max(max(regDataTransfo['V_PHASE_B'].dropna().get_values()),max(regDataTransfo['V_PHASE_A'].dropna().get_values()),max(regDataTransfo['V_PHASE_C'].dropna().get_values()),BORNE_MAX))
    except:
        maxT = BORNE_MAX
    
    regDataTransfo = regDataTransfo.drop(index=regIndex)
    A = go.Scatter(
        x=xRange,
        hoverinfo='text+y+x',
        y=regDataTransfo['V_PHASE_A'],
        name='A',
        mode='markers',
        marker=dict(
            color=COLOR_PHASE_A,
            size = 10
        ),
        text=regDataTransfo['CED_LCLCL']
    )
    B = go.Scatter(
        x=xRange,
        hoverinfo='text+y+x',
        y=regDataTransfo['V_PHASE_B'],
        name='B',
        mode='markers',
        marker=dict(
            color=COLOR_PHASE_B,
            size = 10
        ),
        text=regDataTransfo['CED_LCLCL']
    )
    C = go.Scatter(
        x=xRange,
        hoverinfo='text+y+x',
        y=regDataTransfo['V_PHASE_C'],
        name='C',
        mode='markers',
        marker=dict(
            color=COLOR_PHASE_C,
            size = 10
        ),
        text= regDataTransfo['CED_LCLCL']
    )
    regtext= "{0}<br>{1}".format(ced_lclcl,phase)
    REG = go.Scatter(
        hoverinfo='text',
        x=[regX]*3,
        y=[minT-BANDE_MORTE,VOLT_SETPOINT,maxT+BANDE_MORTE],
        line=dict(
                color= COLOR_TRANSFO_HOVERLABEL2,
                width= 5,
                ),
        name='REG',
        mode='markers+lines',
        marker=dict(
            symbol=41,
            color=COLOR_TRANSFO_HOVERLABEL2,
            size = 15
        ),
        text=regtext
        
    )
      
        
    BorneMax = go.Scatter(
                hoverinfo='none',
                showlegend = False,
                x=xRange,
                y=[BORNE_MAX] * len(regDataTransfo),
                fill='none',
                marker=dict(
                        color=COLOR_REG_LIMIT
                        )
                )
                
    BorneMax2 = go.Scatter(
                hoverinfo='none',
                showlegend = False,
                x=xRange,
                y=[BORNE_MAX+BANDE_MORTE] * len(regDataTransfo),
                fill='none',
                marker=dict(
                        color=COLOR_REG_BAD
                        )
                )
    
    BorneMin = go.Scatter(
                hoverinfo='skip',
                showlegend = False,
                x=xRange,
                y=[BORNE_MIN] * len(regDataTransfo),
                fill='none',
                marker=dict(
                        color=COLOR_REG_LIMIT
                        )
                )
    
    BorneMin2 = go.Scatter(
                hoverinfo='skip',
                showlegend = False,
                x=xRange,
                y=[BORNE_MIN-BANDE_MORTE] * len(regDataTransfo),
                fill='none',
                marker=dict(
                        color=COLOR_REG_BAD
                        )
                )
        
    graphData = [A,B,C,REG,BorneMax,BorneMin,BorneMax2,BorneMin2]
    if transfoCED != None:
        try:
            transIndex = regDataTransfo[regDataTransfo.CED_LCLCL == transfoCED].index[0]
            if km:
                transX = regDataTransfo[regDataTransfo.CED_LCLCL == transfoCED].DISTANCE_KM.item()
            else:
                transX = transIndex - regDataTransfo.first_valid_index()
            phase = regDataTransfo.loc[transIndex].PHASE.strip()
            transY = []
            for i in range(len(phase)):
                transY.append(regDataTransfo.loc[transIndex,'V_PHASE_{0}'.format(phase[i])])
            T_CIRCLE = go.Scatter(
                hoverinfo='skip',
                showlegend = False,
                x=[transX]*len(phase),
                y=transY,
                name='Select',
                mode='markers',
                marker=dict(
                    symbol=100,
                    color=COLOR_REG_GOOD_V,
                    line=dict(width=5),
                    size = 15
                )
            )
            graphData.append(T_CIRCLE)
        except:
            None
    lay = go.Layout(
            font=dict(
                    color=COLOR_TEXTE,
                    size = 18,
                    ),
            title=dict(
                    text='Régulateur {0}'.format(ced_lclcl),
                    ),
            showlegend = True,
            autosize=True,
            margin=go.layout.Margin(l=60, r=0, t=40, b=40),
            xaxis=dict(
                    title=dict(
                            text=textX,
                            ),
                    ),
            yaxis=dict(
                    title=dict(
                            text='Tension (V)',
                            ),
                    ),
            paper_bgcolor = COLOR_BACKGROUND,
            hovermode='closest'
        )                        
    
    fig =go.Figure(
        data=graphData,
        layout=lay
    )
    return fig

def textTransGraph(compteur):
    tab = []
    for c in compteur.itertuples():
        string = "Numéro de Serie: {0}<br>Tension A: {1}<br>Tension B: {2}<br>Tension C: {3}<br>Tension MonoPhase: {4}".format(c.NumeroSerie,c.TensionMoyennePhaseA_V,c.TensionMoyennePhaseB_V,c.TensionMoyennePhaseC_V,c.Tension_V)
        tab.append(string)
    return tab

def genererTransfoGraph(ced_lclcl, codeJour):
    global allData
    transKVA = allData[allData['CED_LCLCL'] == ced_lclcl].iat[0,6]
    compteurall = pd.DataFrame()
    compteurall = pd.read_hdf(r'{0}/{1}/15m/table.h5'.format(hertzP,codeJour),where="CED_LCLCL == '{0}'".format(ced_lclcl)).groupby('NumeroSerie')
    graphData = []
    compteurNumber = 0
    for key in compteurall.groups:
        name = 'Compteur {0}'.format(compteurNumber)
        compteur = compteurall.get_group(key)
        compteurS = go.Scatter(
            hoverinfo='text+x+y',
            y=compteur['TensionMoyennePhaseA_V'],
            x=compteur['DateInterval'],
            mode='lines',
            text='{0} Phase: A'.format(name)
        )
        graphData.append(compteurS)
    
        compteur = compteurall.get_group(key)
        compteurS = go.Scatter(
            hoverinfo='text+x+y',
            y=compteur['TensionMoyennePhaseB_V'],
            x=compteur['DateInterval'],
            mode='lines',
            text='{0} Phase: B'.format(name)
        )
        graphData.append(compteurS)
        
        compteur = compteurall.get_group(key)
        compteurS = go.Scatter(
            hoverinfo='text+y+x',
            y=compteur['TensionMoyennePhaseC_V'],
            x=compteur['DateInterval'],
            mode='lines',
            text='{0} Phase: C'.format(name)
        )
        graphData.append(compteurS)
        
        compteur = compteurall.get_group(key)
        compteurS = go.Scatter(
            hoverinfo='text+y+x',
            y=compteur['Tension_V'],
            x=compteur['DateInterval'],
            mode='lines',
            text=name
        )
        graphData.append(compteurS)
        compteurNumber += 1
    lay = go.Layout(
            font=dict(
                    color=COLOR_TEXTE,
                    size = 18,
                    ),
            title='Transformateur {0} KVA:{1}'.format(ced_lclcl,transKVA),
            showlegend = False,
            autosize=True,
            margin=go.layout.Margin(l=60, r=0, t=40, b=50),
            xaxis=dict(
                    title=dict(
                            text='Temps',
                            ),
                    ),
            yaxis=dict(
                    title=dict(
                            text='Tension (V)',
                            ),
                    ),
            paper_bgcolor = COLOR_BACKGROUND,
        )                       
    
    fig =go.Figure(
        data=graphData,
        layout=lay
    )
    return fig

#%%callback
    
@app.callback(Output('tabReg','data'),
              [Input('pourcentage','value'),
               Input('comparaison','value'),
               Input('ced','value'),
               Input('lclcl','value'),
               Input('code','value'),
               Input('jour','value'),
               Input('temps','value'),
               Input('FiltreCat','value')],
              [State('FiltreCat','options')])
def update_data_reg(pourcentage,volt,ced,lclcl,code,codeJour,temps,filtre,filtreTab):
    global allregDataR
    global allregData
    global VOLT_SETPOINT
    global ECART_SETPOINT
    global BORNE_MAX
    global BORNE_MIN
    global CODE_JOUR
    global CODE_TEMPS
    if code != '' and code != None:
        code = int(code)%10
    if CODE_JOUR != codeJour or CODE_TEMPS != temps:
        CODE_JOUR = codeJour
        CODE_TEMPS = temps
        dataread(codeJour,temps)
        RecalculateStatus()
        allregData.sort_values(by='STATUS',ascending=False,inplace=True)
        allregDataR = allregData.to_dict('rows')
    
    
    if not VOLT_SETPOINT == volt or not ECART_SETPOINT == pourcentage:
        VOLT_SETPOINT = volt
        ECART_SETPOINT = pourcentage
        ecart = ((VOLT_SETPOINT/100)*ECART_SETPOINT)
        BORNE_MIN = VOLT_SETPOINT - ecart
        BORNE_MAX = VOLT_SETPOINT + ecart
        RecalculateStatus()
        allregData.sort_values(by='STATUS',ascending=False,inplace=True)
        allregDataR = allregData.to_dict('rows')
        
    if ced == None:
        startWith = '_{0}'.format(lclcl.upper()) 
    else:
        startWith = "{0}_{1}".format(ced,lclcl.upper())
        
    tempdf = allregData[(allregData["CED_LCLCL"].str.contains(startWith))]
    if type(filtre) != str and filtre != None: 
        test = pd.DataFrame()
        for reg in tempdf.CED_LCLCL:
            data = regComment[regComment['REGULATEUR'] == reg]
            data = data.sort_values(by=sortArray,ascending=False)
            try:
                recent = data.iloc[0]
            except: 
                recent = pd.DataFrame(data=np.array([["","","","Aucun commentaire sur ce Régulateur","None",""]]),columns = colComt).iloc[0]
            if recent.Categorie == filtreTab[filtre]['label']:
                test = test.append(tempdf[tempdf.CED_LCLCL == recent.REGULATEUR])
    
        tempdf = test
    
    if(tempdf.empty):
        if code and code == code:
            return allregData[(allregData['STATUS'] == int(code)) | (allregData['STATUS'] == int(code)+10) | (allregData['STATUS'] == int(code)+20) |(allregData['STATUS'] == int(code)+30)].to_dict('rows')

        return allregDataR
    else:
        if code and code == code:
            tempdf = tempdf[(tempdf['STATUS'] == int(code)) | (tempdf['STATUS'] == int(code)+10) | (tempdf['STATUS'] == int(code) + 20) | (tempdf['STATUS'] == int(code) + 30)]
        return tempdf.to_dict("rows")
    
#CallBack for the map

@app.callback(Output('map','figure'),
              [Input('tabTransfo','data'),
               Input('tabReg','data'),
               Input('toggleTransfo','value'),
               Input('TransfoHidMap','children'),
               Input('TransfoHidTab','children')],
               [State('map', 'relayoutData'),
                State('ced','value'),
                State('jour','value'),
                State('temps','value')])
def update_Map(tabdataUse,tabReg,check,mapElem,tabElem,relay,ced,jour,temps):
    global dropLabelTime
    global CED
    
    timeMap = 0
    timeTab = 0
    transfoElem = None
    if mapElem != None:
        timeMap = pd.Timestamp(mapElem[0:mapElem.find('_')]).value
    if tabElem != None:
        timeTab = pd.Timestamp(tabElem[0:tabElem.find('_')]).value
    if timeMap > timeTab:
        transfoElem = mapElem[mapElem.find('_')+1:]
    if timeTab > timeMap:
        transfoElem = tabElem[tabElem.find('_')+1:]
        
    if ced == None:
        ced = 'Toutes les régions'
        lat = 49.9790924214814
        lon = -69.20876546226282 
        zoom = 4.481014211523867
    elif ced == 'LAV':
        lon = -75.74772533091243
        lat = 47.56379010461427
        zoom = 5.970831767566402
    elif ced == 'IDM':
        lon = -60.617713207480676
        lat = 51.265534908778164
        zoom = 4.94364632811161
    elif ced == 'MAT':
        lon = -68.19005965537224
        lat = 49.749894452298065
        zoom = 5.197324220967887
    elif ced == 'ORL':
        lon = -71.25303203959669
        lat = 46.55616601578558
        zoom = 6.6891245699892306
    elif ced == 'SEI':
        lon = -72.99701499679588
        lat = 45.65284715136565
        zoom = 7.22784417180635
    dic = {'autosize': True}
    if relay != None and relay != dic and CED == ced:
        newMapLayout= go.Layout(
                    margin= dict(
                            l=0,
                            r=0,
                            t=40,
                            b=10
                    ),
                    hovermode='closest',
                    title='Map {0} {1} {2}'.format(ced,jour,dropLabelTime[temps]['label']),
                    font=dict(
                        color=COLOR_TEXTE,
                        size = 18,
                        ),
                    mapbox=dict(
                        accesstoken=mapbox_access_token,
                        bearing=0,
                        center=dict(
                            lat=relay['mapbox.center']['lat'],
                            lon=relay['mapbox.center']['lon']
                        ),
                        pitch=0,
                        zoom=relay['mapbox.zoom']
                    ),
                    autosize =True,
                    height= 600,
                    paper_bgcolor = COLOR_BACKGROUND,
                    showlegend = False,
                )
    else:
        CED = ced
        newMapLayout= go.Layout(
                margin= dict(
                        l=0,
                        r=0,
                        t=40,
                        b=10
                ),
                hovermode='closest',
                title='MAP {0} {1} {2}'.format(ced,jour,dropLabelTime[temps]['label']),
                font=dict(
                    color=COLOR_TEXTE,
                    size = 18,
                    ),
                mapbox=dict(
                    accesstoken=mapbox_access_token,
                    bearing=0,
                    center=dict(
                        lat=lat,
                        lon=lon
                    ),
                    pitch=0,
                    zoom= zoom
                ),
                autosize=True,
                height= 600,
                paper_bgcolor = COLOR_BACKGROUND,
                showlegend = False,
            )
    if check:
        return {'data' : selectData(tabdataUse,tabReg,transfoElem),
                'layout': newMapLayout
                }
    else:
        return {'data' : selectData([],tabReg,None),
                'layout': newMapLayout
                }

@app.callback(Output('tabTransfo','data'),
              [Input('ced','value'),
               Input('lclcl','value'),
               Input('tabReg','data')])
def update_data(ced,lclcl,Data):
    global dataUse
    data = pd.DataFrame(Data)
    tempdf = allTransfoData[allTransfoData["REG_RELATE"].isin(data['CED_LCLCL'].tolist())].copy()
    if(tempdf.empty):
        dataUse = alldataUse
    else:
        dataUse = tempdf.to_dict("rows")
    return dataUse
    
@app.callback(Output('tabTransfo','pagination_settings'),
              [Input('tabTransfo','data')])
def update_page(data):
    return {'current_page': 0,
            'page_size': 9}
    
@app.callback(Output('RegSelec','children'),
              [Input('map','clickData'),
              Input('resetReg','n_clicks')])
def regSelectionner(clickData,reset):
    global buttonClickReset
    if clickData != None:
        strData = str(clickData['points'])
        typeStart = strData.find("Type d'appareil: ")
        appType = strData[typeStart+17:typeStart+19]
        if typeStart < 0:
            typeStart = strData.find("Type d")
            appType = strData[typeStart+18:typeStart+20]
        if buttonClickReset != reset:
            buttonClickReset = reset
            reg = None
        elif appType.startswith('R'):
            reg = strData[strData.find('CED_LCLCL: ')+11:strData.find('CED_LCLCL: ')+20] 
        else:
            reg = strData[strData.find("Regulateur relie: ")+18:strData.find("Regulateur relie: ")+27]
        return reg
    else:
        return None
    
@app.callback(Output('V_Graph','figure'),
              [Input('tabReg','data'),
               Input('TransfoHidMap','children'),
               Input('TransfoHidTab','children'),
               Input('toggleKM','value'),
               Input('RegSelec','children')])
def clickMap(dats,mapElem,tabElem,km,ced):  
    timeMap = 0
    timeTab = 0
    transfoElem = None
    if mapElem != None:
        timeMap = pd.Timestamp(mapElem[0:mapElem.find('_')]).value
    if tabElem != None:
        timeTab = pd.Timestamp(tabElem[0:tabElem.find('_')]).value
    if timeMap > timeTab:
        transfoElem = mapElem[mapElem.find('_')+1:]
    if timeTab > timeMap:
        transfoElem = tabElem[tabElem.find('_')+1:]
        
        
    global graphData
    if ced != None:
        return genererRegGraphFig(ced,transfoElem,km)
    fig =go.Figure(
        data=graphData,
        layout=graphlayout
    )
    return fig


@app.callback(Output('Commentaire','value'),
                     [Input('EntrerCom','n_clicks')])
def resetCommentaire(click):
    return ""

@app.callback(Output('tabNoteReg','data'),
              [Input('RegSelec','children'),
               Input('EntrerCom','n_clicks'),
               Input('Delete','n_clicks'),
               Input('tabReg','data')],
               [State('Commentaire','value'),
                State('pourcentage','value'),
                State('comparaison','value'),
                State('jour','value'),
                State('temps','value'),
                State('Type','value'),
                State('Type','options'),
                State('tabNoteReg','derived_virtual_selected_rows'),
                State('tabNoteReg','derived_virtual_data'),
                State('User', 'children'),
                State('FiltreCat','value'),
                State('FiltreCat','options')])
def updateNoteRegu(reg,button,deleteB,tabREG,commentaire,pourcentage,volts,jour,temps,TP,options,dvsr,dvd,userConnected,filtre,tabFiltre):
    global regComment
    global buttonClick
    global buttonClickDelete
    global dropLabelTime
    global sortArray
    
    tabb = pd.DataFrame(tabREG)
    if reg != None:
        tabb = tabb[tabb['CED_LCLCL'] == reg]
    #drop
    if dvsr is not None and deleteB != buttonClickDelete and deleteB != None:
        buttonClickDelete = deleteB
        row = dvd[dvsr[0]]
        user = row['Auteur']
        if user == userConnected or userConnected.lower() == 'admin':
            regComment = pd.read_hdf(DBcomment)
            row2 = regComment[(regComment['Auteur'] == user) & (regComment['Date Du Commentaire'] == row['Date Du Commentaire']) & (regComment['Parametre'] == row['Parametre']) & (regComment['Commentaire'] == row['Commentaire']) & (regComment['REGULATEUR'] == row['REGULATEUR'])]
            print('Delete')
            regComment = regComment.drop(row2.iloc[0].name)
            regComment.to_hdf(DBcomment,key='DB')
            data = regComment.where(regComment.REGULATEUR.isin(tabb.CED_LCLCL)).dropna()
            if type(filtre) != str and filtre != None: 
                data = data.drop_duplicates(subset=['REGULATEUR'],keep='last')
            data = data.sort_values(by=sortArray,ascending=False)
            return data.to_dict("rows")
        
    #Ajout commentaire
    if button != buttonClick and button != None and reg != None:
            buttonClick = button
            regComment = pd.read_hdf(DBcomment)
            regComment = regComment.append(pd.Series(['{0}'.format(userConnected),'{0}'.format(pd.Timestamp('now').date()),'{0}::{1} {2}V {3}V'.format(jour,dropLabelTime[temps]['label'],pourcentage,volts),'{0}'.format(commentaire),'{0}'.format(options[TP]['label']),reg],index=colComt),ignore_index=True)
            regComment.to_hdf(DBcomment,key='DB')
            
    #select regulateur    
    regComment = pd.read_hdf(DBcomment)
    data = regComment.where(regComment.REGULATEUR.isin(tabb.CED_LCLCL)).dropna()
    if type(filtre) != str and filtre != None: 
        data = data.drop_duplicates(subset=['REGULATEUR'],keep='last')
    data = data.sort_values(by=sortArray,ascending=False)
    return data.to_dict("rows")

@app.callback(Output('TransfoHidMap','children'),
              [Input('map','clickData'),
               Input('RegSelec','children')])
def updateHidMap(clickData,reg):
    if clickData != None and reg !=None:
        strData = str(clickData['points'])
        ced_lclcl = strData[strData.find('CED_LCLCL: ')+11:strData.find('CED_LCLCL: ')+20]
        appType = strData[strData.find("Type d'appareil: ")+17:strData.find("Type d'appareil: ")+19]
        if appType.startswith('T'):
            return '{0}_{1}'.format(pd.Timestamp('now'),ced_lclcl)
    return None

@app.callback(Output('TransfoHidTab','children'),
              [Input('V_Graph','clickData'),
               Input('RegSelec','children')])
def updateHidTab(clickData,reg):
    if clickData != None and reg !=None:
        strData = str(clickData['points'])
        ced_lclcl = strData[strData.find("'text': ")+9:strData.find("'text': ")+18]
        return '{0}_{1}'.format(pd.Timestamp('now'),ced_lclcl)
    return None

@app.callback(Output('V_Graph_Compteur','figure'),
              [Input('TransfoHidMap','children'),
               Input('TransfoHidTab','children'),
               Input('jour','value'),
               Input('RegSelec','children')])
def clickTabReg(mapElem,tabElem,codeJour,reg):
    global graphData
    fig =go.Figure(
        data=graphData,
        layout=graphlayout2
    )
    timeMap = 0
    timeTab = 0
    if mapElem != None:
        timeMap = pd.Timestamp(mapElem[0:mapElem.find('_')]).value
    if tabElem != None:
        timeTab = pd.Timestamp(tabElem[0:tabElem.find('_')]).value
    if timeMap > timeTab:
        return genererTransfoGraph(mapElem[mapElem.find('_')+1:], codeJour)
    if timeTab > timeMap:
        return genererTransfoGraph(tabElem[tabElem.find('_')+1:], codeJour)
    
    return fig

@app.callback(Output('Comment','style'),
              [Input('RegSelec','children')])
def showCommentOption(reg):
    if reg == None:
        return {'display':'none'}
    else:
        return {'display':'grid'}
    
@app.callback(Output('waw', 'children'),
              [Input('enter','n_clicks')],
              [State('User','value'),
               State('F','children')])
def login(click,user,label):
    print(click,user)
    global userConnect
    if label == "Mot de Passe":
        if user == '123':
            return appLayout
        else:
            return connectLayout
    elif user and user.lower() != 'admin':
        userConnect= user
        return appLayout
    elif user.lower() == 'admin':
        userConnect= user
        return MDPconnectLayout
    else:
        return connectLayout

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    global userConnect
    if pathname == '/regulateur/testing':
        userConnect = 'Test'
        return appLayout 
    else:
        return testLayout
    
@app.callback(Output('User', 'children'),
              [Input('page-content', 'children')])
def testUser(pathname):    
    return userConnect

if __name__ == '__main__':
    print(pd.Timestamp('now'))
    app.run_server(debug=True)