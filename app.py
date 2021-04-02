# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

import gunicorn
import time
import datetime

import math
import numpy as np

import pandas as pd
import plotly.graph_objs as go

df_choro = pd.read_csv("data/ini_choropleth_data.csv").replace(':',np.nan).replace('Germany including former GDR','Germany').replace(
    'Kosovo (under United Nations Security Council Resolution 1244/99)', 'Kosovo')

df_less15 = df_choro[df_choro['AGE']=="Less than 15 years"].copy().reset_index()
df_more65 = df_choro[df_choro['AGE']=="65 years or over"].copy().reset_index()
df_total = df_choro[df_choro['AGE']=="Total"].copy().reset_index()

df_less15['Value'] = df_less15['Value'].str.replace(' ','').astype(float)
df_more65['Value'] = df_more65['Value'].str.replace(' ','').astype(float)
df_total['Value'] = df_total['Value'].str.replace(' ','').astype(float)

#From absolute to percentages of total population:
df_less15['Value']=(df_less15['Value']/df_total['Value'])*100
df_more65['Value']=(df_more65['Value']/df_total['Value'])*100

def choropleth_data(year, segment):
    
    if segment=='Less than 15 years':
        df = df_less15[df_less15['TIME']==year].copy()
        zmin = math.floor(df_less15.Value.min())
        zmax = 35
        colorscale = 'deep'

        
    elif segment == '65 years or over':
        df = df_more65[df_less15['TIME']==year].copy()
        zmin = math.floor(df_more65.Value.min())
        zmax = math.ceil(df_more65.Value.max())
        colorscale = 'speed' #'Purpor',

    
    
    data_choropleth = dict(type='choropleth',
                       locations=df['GEO'],  #There are three ways to 'merge' your data with the data pre embedded in the map
                       locationmode='country names',
                       z=df['Value'],
                       text=df['GEO'],
                       colorscale= colorscale,
                       zmin = zmin,
                       zmax = zmax,
                       colorbar_ticksuffix = '%',
                       #dragmode = False
                      )
    if segment == 'Less than 15 years':
        layout_choropleth = dict(geo=dict(scope='europe',  #default
                                      projection=dict(type='orthographic'
                                                     ),
                                      #showland=True,   # default = True
                                      
                                      landcolor='white',
                                      showlakes=False,#lakecolor='white',
                                      showocean=True,   # default = False
                                      oceancolor='rgba(0,0,0,0)',
                                      bgcolor='#f9ffff',
                                      resolution = 50,
                                      center=dict(lon=12, lat=50),
                                      
                                     ),
                             
                             dragmode=False,
                             title=dict(text='Percentage of population younger than 15 on year ' + str(year),
                                        font_size=20,
                                        font_color="#002B6B",
                                        font_family="Glacial Indifference",
                                        x=.5 # Title relative position according to the xaxis, range (0,1)
                                       )
                            )
    else:
        layout_choropleth = dict(geo=dict(scope='europe',  #default
                              projection=dict(type='orthographic'
                                             ),
                              #showland=True,   # default = True
                              
                              landcolor='white',
                              showlakes=False,#lakecolor='white',
                              showocean=True,   # default = False
                              oceancolor='rgba(0,0,0,0)',
                              bgcolor='#f9ffff',
                              resolution = 50,
                              center=dict(lon=12, lat=50),
                              
                             ),
                     
                     dragmode=False,
                     title=dict(text='Percentage of population that is 65 or older on year ' + str(year),
                                font_size=20,
                                font_color="#002B6B",
                                font_family="Glacial Indifference",
                                x=.5 # Title relative position according to the xaxis, range (0,1)
                               )
                    )
    return [data_choropleth, layout_choropleth]


subset_options_choro = [
    {'label': 'Less than 15 years', 'value': 'Less than 15 years'},
    {'label': '65 years or over', 'value': '65 years or over'}
]


df_pyramids=pd.read_csv('data/poppyramiddata v2.csv').replace(':',0).replace('Germany (until 1990 former territory of the FRG)','Germany').replace(
    'Kosovo (under United Nations Security Council Resolution 1244/99)', 'Kosovo')

country_options_pyramids = [
    dict(label= country, value=country)
    for country in np.sort(df_pyramids['GEO'].unique())]

df_fertility = pd.read_csv('data/FertilityRatesTotal.csv').replace(':',np.nan).replace('').replace('Germany including former GDR','Germany').replace(
    'Kosovo (under United Nations Security Council Resolution 1244/99)', 'Kosovo')

df_fertility['TIME']=df_fertility['TIME'].astype(int)
df_fertility['Value']=df_fertility['Value'].astype(float)
df_fertility=df_fertility[['TIME','GEO','Value']]

country_options_fertility= [dict(label= country, value=country)
    for country in np.sort(df_fertility['GEO'].unique())]



initial_country_options_fertility=np.sort(['Portugal','Netherlands','United Kingdom','France','Ireland',
                                   'Bulgaria', 'Germany'])

df_fertility2 = pd.read_csv('data/FertilityForeignNative2010on.csv').replace(':',np.nan).replace('').replace('Germany including former GDR','Germany').replace(
    'Kosovo (under United Nations Security Council Resolution 1244/99)', 'Kosovo')

df_fertility2['Value'] = df_fertility2['Value'].str.replace(' ','').astype(float)
df_fertility2_total = df_fertility2[df_fertility2['CITIZEN']=='Total'].reset_index().copy()[['TIME','GEO','CITIZEN','Value']]
df_fertility2_reporting = df_fertility2[df_fertility2['CITIZEN']=='Reporting country'].reset_index().copy()[['TIME','GEO','CITIZEN','Value']]
df_fertility2_foreign = df_fertility2[df_fertility2['CITIZEN']=='Foreign country'].reset_index().copy()[['TIME','GEO','CITIZEN','Value']]

country_options_fertility2= [dict(label= country, value=country)
    for country in np.sort(df_fertility2['GEO'].unique())]


df_immigration = pd.read_csv('data/TotalPopulation_NativeForeign_BroadAgeGroups.csv').replace('Germany (until 1990 former territory of the FRG)','Germany')

country_options_migration_lines=[dict(label= country, value=country)
    for country in np.sort(df_immigration['GEO'].unique())]

immiaux = df_immigration[(df_immigration['AGE']=='Total')&(df_immigration['SEX']=="Total")&(df_immigration['TIME']==2019)&(df_immigration['C_BIRTH']=='Total')].replace(':',np.nan)
immiaux['Value'] = immiaux['Value'].str.replace(' ','').astype(float)
c_o_m_list = np.sort(immiaux[~immiaux['Value'].isna()]['GEO'])

country_options_migration_bars=[dict(label=country,value=country) for country in c_o_m_list]

def inm_preprocessing(df_input_immigration,country):
    
    df_input_immigration = df_immigration.copy().replace(':',np.nan)
    df_input_immigration = df_input_immigration[df_input_immigration['AGE'] == 'Total']
    df_input_immigration =df_input_immigration[df_input_immigration['SEX'] == 'Total']

    df_input_immigration['Value'] = df_input_immigration['Value'].str.replace(' ','')
    #df_input_immigration['Value'] = df_input_immigration['Value'].str.replace(':','0')
    df_input_immigration['Value'] = df_input_immigration['Value'].astype(float)
    
    cb = ['Reporting country','Foreign country']
    df_input_immigration = df_input_immigration[df_input_immigration['C_BIRTH'].isin(cb)]
    
    df_input_immigration = df_input_immigration[df_input_immigration['GEO'] == country]
    
    return df_input_immigration




def preprocess_poppyramid(df_input, country, year):

    df = df_input.copy()
    df = df[df['GEO'] == country]

    df['TIME'] = df['TIME'].astype(int)
    df = df[df['TIME'] == year]

    df = df[df['AGE'] != 'Total']
    df = df[df['AGE'] != 'Open-ended age class']
    df = df[df['AGE'] != 'Unknown']

    df = df[df['SEX'] != 'Total']
    dfm = df[df['SEX'] == 'Males']
    dfm = dfm.pivot(index = 'AGE', columns = 'SEX', values = 'Value')
    dfm = dfm.reset_index()

    dff = df[df['SEX'] == 'Females']
    dff = dff.pivot(index = 'AGE', columns = 'SEX', values = 'Value')
    dff = dff.reset_index()

    df = pd.merge(dfm, dff, on="AGE")

    df['AGE'] = df['AGE'].str.replace(' years', '')
    df['AGE'] = df['AGE'].str.replace(' year', '')
    df['AGE'] = df['AGE'].str.replace('Less than 1', '0')
    df['Males'] = df['Males'].str.replace(' ', '')
    df['Females'] = df['Females'].str.replace(' ', '')

    df['AGE'] = df['AGE'].astype(int)
    df['Males'] = df['Males'].astype(int)
    df['Females'] = df['Females'].astype(int)

    df = df.sort_values(by=['AGE'])

    bins = pd.cut(df['AGE'], list(range(-1,105,5)))
    df = df.groupby(bins).sum()
    df = df.rename(columns = {'AGE' : 'Age'})
    df = df.reset_index()
    df['AGE'] = df['AGE'].astype(str)

    beg = list(range(0,105,5))
    end = list(range(4,105,5))

    ranges = []
    for i in range(len(beg)):
        stri = str(beg[i]) + '-' + str(end[i])
        ranges.append(stri)
    
    df['new_age_ranges'] = ranges
    
    return df


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = html.Div(#style={'backgroundColor':'#f9ffff'}, 
                      children=[
    html.Div([
    html.H1("Europe's ageing population - What's this phenomenon?",
            style={
                'color': '#002B6B',
                'font-family': 'Tw Cen MT',
                'fontSize': 45,
                
                'margin-left':'100px',
                }),
    ],style={'backgroundImage':'url(https://i.imgur.com/OgizMtB.png)', 'margin-left':'100px'}),#'url(https://i.imgur.com/yOurYHn.png)',}
    
                 
    dcc.Tabs(id='tabs',children = [
        dcc.Tab(id='Introduction',label='Introduction',style={'font-family':'Tw Cen MT', 'color':'#002B6B', 'font-size':20},
                selected_style={'font-family':'Tw Cen MT', 'color':'#002B6B', 'font-size':25},
                children=[html.Div(id='tab1content', children=[
                    html.Div([
                    dcc.Graph(id='choropleth_map'),
         
            html.Div([
                html.Div([
                    html.Br(),
                    dbc.Button(children='Play', id = 'play-button', n_clicks=0,
                       className="mr-1", color = 'primary',
                        style={'width':'100%', 'bottom':'10px'},
                        ),
            
            ], style={'width':'10%', 'bottom':'10px'}),
                
                
                html.Div([
                    html.Div([
                    dcc.RadioItems(
            id='subset_drop',
            options=subset_options_choro,
            value='Less than 15 years',
            labelStyle={'display': 'inline-block'},
            style={'font_family':'Glacial Indifference', 'margin-left': '5px', 'width':'100%'},
            inputStyle={"margin-left": "28px", 'margin-right':'10px'}
            ),
          ], style={'width':'100%'}),
                    
                    html.Div([
            dcc.Slider(
                id='year_slider_choro',
                min=1960,
                max=2020,
                step=10,
                marks={
                i : str(i) for i in [1960, 1970, 1980, 1990, 2000, 2010, 2015, 2020]
                },
                value=1960,
                updatemode='drag',
            ),
            ], style={'width':'100%', 'margin-left':'15px'}),
                    ], style={'width':'100%'}),
                ], style={'display':'flex'}),
            
            html.Br(),
            html.Br(),
            
            
            
            dcc.Interval(id='auto-stepper',
            interval=1.5*1000, # in milliseconds
            n_intervals=0,
            max_intervals=7,
            disabled = True
            ),
    ], style= {'width': '58%'}),
                html.Div([
                    html.Br(),
                    html.Div('Over the past few decades, better healthcare services and the absence of major conflicts have contributed to a higher life expectancy among Europe’s nations. Combined with lower birth rates, this is resulting in a continent with a population that is getting older and inverting its nations’ population pyramids. This phenomenon, known as the Ageing of Europe, carries many socio-economic consequences, such as future overloading on the health and social care services or a higher pressure on pensions’ systems.',
                     style={
                         'textAlign':'justify',
                         'font-family': 'Glacial Indifference',
                         'color': '#002B6B',
                         'fontSize': 20,
                         'marginBottom': '1.5em',
                         }),
                    html.Div('Are there solutions to mitigate this problem or to minimize its long-term consequences? Is immigration a solution, or are policies that incentive natality preferred? Here we explore some sides of this demographic problem recurring to data made available by the European portal Eurostat.',
                   style={
                         'textAlign':'justify',
                         'font-family': 'Glacial Indifference',
                         'color': '#002B6B',
                         'fontSize': 20,
                         }
                   ),
    ], style={'width': '40%', 'vertical-align':'middle', 'margin-left':'85px', 'margin-right':'65px'}),
                ],
                style={'display': 'flex'}),
            
           
            html.Div([
     html.Footer(html.Img(src='https://i.imgur.com/EqvSPMJ.png',
                   style={'display': 'block', 'margin-left': 'auto','margin-right': 'auto', 'width': '100%'})
                   ), 
    ]),]
            ),
                    
            
         
                
        dcc.Tab(id='Fertility',label='Fertility', style={'font-family':'Tw Cen MT', 'color':'#002B6B', 'font-size':20},
                selected_style={'font-family':'Tw Cen MT', 'color':'#002B6B', 'font-size':25},
                children=[
                    html.Div(id='tab2content',children=[
                        html.Div([
            dcc.Dropdown(
                            id='country_drop_fertility',
                            options=country_options_fertility,
                            value=initial_country_options_fertility,
                            multi=True,
                            style={'font_family':'Glacial Indifference'}, # "overflow-y":"scroll"},
                        ),
            dcc.Graph(id='fertility-lines'),
            
            html.Div([
            dcc.RangeSlider(
                        id='range_year_slider_fertility',
                        min=1960,
                        max=2019,
                        value=[1960, 2019],
                        marks={i:str(i) for i in [x for x in range(1960,2020,5)]+[2019]
                               },
                        updatemode='drag',
                        step=1
    ),
            ], style={'margin-left': '15px'}),
                        
            html.Br(),
            html.Br(),
            ], style={'width':'52%'}),
                        html.Div([
                    
            dcc.Dropdown(id='country_drop_fertilitybars',
                            options=country_options_fertility2,
                            value='Switzerland',
                            multi=False,
                            style={'font_family':'Glacial Indifference'},
                            ),
            
            
            dcc.Loading(
                type='cube',
                color = '#6facf4',
                children = dcc.Graph(id='fertility-bars')
                
                ),
            
            
            ], style={'width':'48%'}),
                        
            ], style={'display':'flex'}),
            
            html.Br(),
            html.Div([
                    html.Div('Regarding fertility rates, the average number of births per woman varies from country to country within Europe, but has been generally decreasing over the past few decades across the continent. Consequently, the fertility rates are far from the minimum generation renewal standard, set at 2.1 children per woman, considered necessary in developed countries to maintain the population in the long run.',
                     style={
                         'textAlign':'justify',
                         'font-family': 'Glacial Indifference',
                         'color': '#002B6B',
                         'fontSize': 20,
                         'marginBottom': '1.5em'
                         }),
                    html.Div('There are factors of social, economic and cultural nature that explain such low birth rates all across Europe. Individual and behavioural decisions linked to family planning, also considering the reality of careers and labour market, education and well-being are some of the factors that influence these values.',
                   style={
                         'textAlign':'justify',
                         'font-family': 'Glacial Indifference',
                         'color': '#002B6B',
                         'fontSize': 20,
                         'marginBottom': '1.5em'
                         }
                   ),
                    html.Div('Despite this, there are some European countries that are close to the target value, such as Ireland or France. On the other hand, countries like Ukraine, Spain and Italy have been registering some of the lowest values on Europe on recent years. There are also some countries that rely heavily on births from foreign parents, which is explained by the substantial reception of younger migrants of childbearing age.',
                   style={
                         'textAlign':'justify',
                         'font-family': 'Glacial Indifference',
                         'color': '#002B6B',
                         'fontSize': 20,
                         }
                   ),
    ], style={'width': '98%', 'vertical-align':'middle', 'margin-left': 'auto','margin-right': 'auto'}),
            
             html.Div([
     html.Footer(html.Img(src='https://i.imgur.com/EqvSPMJ.png',
                   style={'display': 'block', 'margin-left': 'auto','margin-right': 'auto', 'width': '100%'})
                   ),
             ])
        ]
                    
                    ),
        
        
        
        dcc.Tab(id='Migration',label='Migration',  style={'font-family':'Tw Cen MT', 'color':'#002B6B', 'font-size':20}, 
                selected_style={'font-family':'Tw Cen MT', 'color':'#002B6B', 'font-size':25},
                children=[
                    
                    html.Div(id='tab3content',children=[
                    
            html.Div([
                
                html.Div([
                    
                    html.Div([
                        
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                        html.Br(),
                    html.Div("\n Although migration may play an important role in Europe's population dynamism, it is unlikely that it can reverse the ongoing trend of population ageing.",
                     style={
                         'textAlign':'justify',
                         'font-family': 'Glacial Indifference',
                         'color': '#002B6B',
                         'fontSize': 20,
                         'marginBottom': '1.5em'
                         }),
                    html.Div('If migration policies are carried out successfully, European countries may have several benefits, namely in combating an aging population across the continent, and in some regions in particular, by reducing demographic imbalances and boosting labour markets, which creates benefits for the economy of these countries.',
                   style={
                         'textAlign':'justify',
                         'font-family': 'Glacial Indifference',
                         'color': '#002B6B',
                         'fontSize': 20,
                         }
                   ),
                    
    ], style={'width': '40%', 'vertical-align':'middle', 'margin-left': 'auto','margin-right': 'auto'}),
                    html.Div([
                    
                    dcc.Loading(
                        
                        type='dot',
                        children=dcc.Graph(id='migration-lines')
                        
                        ),
                    dcc.Dropdown(
                        id='country_drop_migration_lines',
                        options=country_options_migration_lines,
                        value='Portugal',
                        multi=False
                    ),
                    ], style={'width':'52%', 'margin-right':'10px', 'margin-left':'10px'}),
                                         
                    
            ], style={'display':'flex'}),  
                
                html.Br(),
                html.Div([
                html.Div('However, recent migration trends have affected Europe unevenly. According to Eurostat data, some more peripherical countries such as Bulgaria or Portugal, as well as central parts of France have seen their population decreasing. Other regions, such as the case of some German and Swedish cities, have had a very considerable inflow of migrants, mainly from outside Europe.',
                   style={
                         'textAlign':'justify',
                         'font-family': 'Glacial Indifference',
                         'color': '#002B6B',
                         'fontSize': 20,
                         }
                   ),
                ], style={'margin-left':'25px', 'margin-right':'15px'}),
                    
                    html.Br(),
                    dcc.Loading(
                        
                        type='graph',
                        children=dcc.Graph(id='migration-bars')
                        
                        ),
                    
                    html.Div([
                    dcc.Dropdown(
                        id = 'country_drop_migration_bars',
                        options = country_options_migration_bars,
                        value=['Portugal','France','Switzerland','Germany','United Kingdom'],
                        multi=True
                        
                        ),
                    html.Div([
                        html.Div([
                    dcc.Checklist(
                        id='stacked-bars',
                        options=[{'label':'Stack', 'value':'Stack'}],
                        value=[],
                        inputStyle={"margin-right": "10px"}
                        ),
                    ], style={'width':'30%'}),
                        
                        html.Div([
                    dcc.RadioItems(
                        id='radio-bars',
                        options=[
                            {'label':'Absolute','value':'Absolute'},
                            {'label':'Percentages','value':'Percentages'}],
                        value='Percentages',
                        inputStyle={"margin-left": "28px", 'margin-right':'10px'}
                        ),
                    ], style={'width':'30%'}),
                        
                    ], style={'display':'flex', 'margin-left':'500px'}),
                    
                    html.Div([
                     dbc.Button(
                         'Submit changes', id = 'bars-button', n_clicks=0,
                         className="mr-1", color = 'primary'
                         
                         ),
                     ], style={'margin-left':'600px'}),
                    
                     ], style={'margin-left': '10px'}),
                    ]),
                    
            
             html.Div([
     html.Footer(html.Img(src='https://i.imgur.com/EqvSPMJ.png',
                   style={'display': 'block', 'margin-left': 'auto','margin-right': 'auto', 'width': '100%'})
                   ),
             ]),])
            
        ]
                    
                    ),
        
        dcc.Tab(id='Population Pyramids', label='Population Pyramids',  style={'font-family':'Tw Cen MT', 'color':'#002B6B', 'font-size':20}, 
                selected_style={'font-family':'Tw Cen MT', 'color':'#002B6B', 'font-size':25},
                children=[
                    html.Div(id='tab4content',children=[
                    html.Br(),
                    html.Br(),
                    html.Div("On the Population Pyramids we find the result of past birth rates. In general, European countries have a strong proportion of the population over 45 years old. The baby-boomers generation’s individuals born after the Second World War (after 1945) are still present, as well as those born between 1965 and 1980, the so-called Generation X, children of the baby-boomers.",
                     style={
                         'textAlign':'justify',
                         'font-family': 'Glacial Indifference',
                         'color': '#002B6B',
                         'fontSize': 22,
                         'marginBottom': '1.5em',
                         }),
                    html.Div('Subsequently, there has been a sharp decline in birth rates in almost every European country, leading to shorter age classes at the base of the pyramids – a problem that affects south European countries the most: Greece, Italy, Portugal or Spain all have shorter pyramid bases.',
                   style={
                         'textAlign':'justify',
                         'font-family': 'Glacial Indifference',
                         'color': '#002B6B',
                         'fontSize': 22,
                         }
                   ),
                html.Br(),
                html.Br(),
    ], style={'width': '98%', 'vertical-align':'middle', 'margin-left': 'auto','margin-right': 'auto'}),
                html.Div([
                    html.Div([
            dcc.Dropdown(
                id='country_drop1',
                options=country_options_pyramids,
                value='Portugal',
                multi=False,
                style={'font_family':'Glacial Indifference'},
                ),
            dcc.Loading(
            id="loading-poppyramid1",
            type="dot",
            children=dcc.Graph(id='pop_pyramid1')
            ),
            ],style={'width': '32%'}),
                     html.Div([
            dcc.Dropdown(
                id='country_drop2',
                options=country_options_pyramids,
                value='Ireland',
                multi=False,
                style={'font_family':'Glacial Indifference'},
                ),
            dcc.Loading(
            id="loading-poppyramid2",
            type="dot",
            children=dcc.Graph(id='pop_pyramid2')
            ),
            
            ],style={'width': '32%'}),
                      html.Div([
            dcc.Dropdown(
                id='country_drop3',
                options=country_options_pyramids,
                value='France',
                multi=False,
                style={'font_family':'Glacial Indifference'},
                ),
            dcc.Loading(
            id="loading-poppyramid3",
            type="dot",
            children=dcc.Graph(id='pop_pyramid3')
            ),
            ]
            ,style={'width': '32%'}              ),
                ], style={'display': 'flex'}),
        
            html.Br(),
        
        
            html.Br(),
        
        html.Div([
            dcc.Slider(
                id='year_slider',
                min=2011,
                max=2020,
                marks={
                2011: '2011',
                2012: '2012',
                2013: '2013',
                2014: '2014',
                2015: '2015',
                2016: '2016',
                2017: '2017',
                2018: '2018',
                2019: '2019',
                2020: '2020',
                },
                value=2020,
                step=1,
                updatemode='drag',
                included=False,
                
            ),
            ], style={'margin-left':'20px', 'margin-right':'10px'}),
            
                 
             html.Div([
     html.Footer(html.Img(src='https://i.imgur.com/EqvSPMJ.png',
                   style={'display': 'block', 'margin-left': 'auto','margin-right': 'auto', 'width': '100%'})
                   ),
             ])
        ]
                    
                    ),
        
        dcc.Tab(id='Conclusions',label='Conclusions',  style={'font-family':'Tw Cen MT', 'color':'#002B6B', 'font-size':20}, 
                selected_style={'font-family':'Tw Cen MT', 'color':'#002B6B', 'font-size':25},
                children=[
                    
                    html.Div(id='tab5content',children=[dcc.Graph(
                figure={
                    'data': [
                        {'x': [1, 2, 3], 'y': [2, 4, 3],
                            'type': 'bar', 'name': 'SF'},
                        {'x': [1, 2, 3], 'y': [5, 4, 3],
                         'type': 'bar', 'name': u'Montréal'},
                    ]
                }
            ),
             html.Div([
                    html.Br(),
                    html.Br(),
                    html.Div("While Europe tries to stem population decline with policies to increase birth rates, some experts argue that low birth rates are a reason to celebrate. To defend this theory, they remember that this decline is also due to the recent balance in the role of gender and that a country does not need to have high birth rates to have economic growth. In addition, having fewer children results in a drastic reduction in greenhouse gas emissions, by significantly reducing consumption. Today we live more years in a healthy way, we can work later in life and another argument is that a smaller population helps to increase the per capita economic indicators, directly associated to the wealth of the country and its inhabitants. ",
                     style={
                         'textAlign':'justify',
                         'font-family': 'Glacial Indifference',
                         'color': '#002B6B',
                         'fontSize': 20,
                         'vertical-align':'middle', 'margin-left': '15px','margin-right': '15px',
                         'marginBottom': '1.5em',
                         }),
                    html.Div('In another aspect, population movements within Europe tend to be related to favourable job and career and economic opportunities. In this sense, one of the most usual internal movements is that which happens between educated young professionals from countries in the southern part of the continent to countries in north-western Europe, which has been stressed in recent years mainly after the economic crisis.',
                   style={
                         'textAlign':'justify',
                         'font-family': 'Glacial Indifference',
                         'color': '#002B6B',
                         'fontSize': 20,
                         'vertical-align':'middle', 'margin-left': '15px','margin-right': '15px',
                         'marginBottom': '1.5em',
                         }
                   ),
                    html.Div('Therefore, migration within Europe and between other continents and Europe can help create benefits for both sides. Despite this, the paradigm is a little more complex, existing factors such as the education of migrants, social, cultural and religious factors, natural and warlike events in the equation. Regardless of being widely defended by some economists and sociologists, migration is still not seen fairly as an alternative to the demographic crisis in Europe. This issue is highly relevant and is therefore used in political disputes, which are not always based on rational and fair arguments. ',
                   style={
                         'textAlign':'justify',
                         'font-family': 'Glacial Indifference',
                         'color': '#002B6B',
                         'fontSize': 20,
                         'vertical-align':'middle', 'margin-left': '15px','margin-right': '15px',
                         'marginBottom': '1.5em',
                         }
                   ),
                    html.Div('In addition, the challenges of an aging population are not exclusive to Europe. If, on the one hand, the aging of the working population is not so pronounced in the United States, there are world powers such as China and Japan, for example, where this aging phenomenon occurs. In the rest of the world, population growth has been a reality and will continue to be in the coming decades mainly due to emerging countries and also underdeveloped countries, with high birth rates. ',
                   style={
                         'textAlign':'justify',
                         'font-family': 'Glacial Indifference',
                         'color': '#002B6B',
                         'vertical-align':'middle', 'margin-left': '15px','margin-right': '15px',
                         'fontSize': 20,
                         }
                   ),
                    ]),
                         html.Div([
     html.Footer(html.Img(src='https://i.imgur.com/EqvSPMJ.png',
                   style={'display': 'block', 'margin-left': 'auto','margin-right': 'auto', 'width': '100%'})
                   ), 
                 ])
            
             ]
                        
                        )
                    ])
        ]),
])
        
### INTRODUCTION TAB CALLBACKS
@app.callback(
    Output('year_slider_choro', 'value'),
    [Input('auto-stepper', 'n_intervals'),
     Input('auto-stepper', 'disabled'),
     Input('play-button', 'n_clicks')])

def on_click(n_intervals, disabled, n_clicks):
    if disabled is False:
        if n_intervals in [0, 1, 2, 3, 4, 5]:
            return 1960 + n_intervals*10
        
        elif n_intervals==6:
            return 2015
        elif n_intervals==7: 
            return 2020
        
    if disabled is True:
         if n_clicks%2==0: return 1960
         if n_clicks%2!=0: raise PreventUpdate

@app.callback(Output('auto-stepper','n_intervals'),
                     [Input('play-button','n_clicks')])

def on_click2(n_clicks):
    if n_clicks%2==1:
        raise PreventUpdate
    if n_clicks%2==0:
        return 0

@app.callback(Output('auto-stepper','disabled'),
                     [Input('play-button','n_clicks')])

def on_click3(n_clicks):
    if n_clicks%2==1:
        return False
    if n_clicks%2==0:
        return True

@app.callback(Output('play-button','children'),
              [Input('play-button','n_clicks')])

def on_click4(n_clicks):
    if n_clicks%2==1:
        return "Reset"
    if n_clicks%2==0:
        return "Play"
    


@app.callback(
    Output('choropleth_map', 'figure'),
    [Input('subset_drop', 'value'),
      Input('year_slider_choro', 'value')]
)

def update_graph_choro(subset, year):
    
    auxchoro = choropleth_data(year,subset)
    
    data_choropleth = auxchoro[0]
    layout_choropleth = auxchoro[1]
    
    fig_choropleth = go.Figure(data=data_choropleth, layout=layout_choropleth)
    
    
    return fig_choropleth

#### FERTILITY CALLBACKS

@app.callback(
    Output('fertility-lines','figure'),
    [Input('country_drop_fertility','value'),
     Input('range_year_slider_fertility','value')]
    
    )
def fertility_lines_update(countries,years):
    
    df_fertility_years= df_fertility[(df_fertility['TIME'] >= years[0]) & (df_fertility['TIME'] <= years[1])]
    data_fertility = [dict(type='scatter',
                        
                        x=df_fertility_years.loc[df_fertility['GEO'] == country]['TIME'],
                        y=df_fertility_years.loc[df_fertility['GEO'] == country]['Value'],
                        
                        #text=df.loc[df['GEO'] == country]['GEO'],
                        mode='lines',
                        name=country
                    ) 
                for country in countries]

    layout_fertility = dict(title=dict(text= 'Fertility Rates'),
              xaxis=dict(title='Years'
                        
                        ),
              yaxis=dict(title='Fertility Rate'),
              title_font_family='Glacial Indifference', title_font_color='#002B6B',
              plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgba(0,0,0,0)',
             )

    figure = go.Figure(data=data_fertility, layout=layout_fertility)

    figure.update_yaxes(
        range=[1,4.2],  # sets the range of xaxis
        constrain="domain",  # meanwhile compresses the xaxis by decreasing its "domain"
        )      
    return figure

@app.callback(Output('fertility-bars','figure'),
    [Input('country_drop_fertilitybars','value')])

def fertility_bars_update(country):
    
    time.sleep(1)
    years = df_fertility2.TIME.unique()
    
    fig = go.Figure()

    fig.add_trace(go.Bar(x=years,
                    y=[x for x in df_fertility2_reporting[df_fertility2_reporting['GEO']==country]['Value']],
                    name='Native parents',
                    marker_color='#b0d7ac'
                    ))
    fig.add_trace(go.Bar(x=years,
                    y=[x for x in df_fertility2_foreign[df_fertility2_foreign['GEO']==country]['Value']],
                    name='Foreign parents',
                    marker_color='#6facf4'
                    ))

    fig.update_layout(
        title='Number of births in ' + country + ' during the last decade',
        title_font_family='Glacial Indifference', title_font_color='#002B6B',
        plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgba(0,0,0,0)',
        xaxis_tickfont_size=14,
        xaxis = dict(tickvals = [i for i in range(2010,2020)],                
                     ticktext = [i for i in range(2010,2020)],
                     ),
        
        yaxis=dict(
            title='Number of births',
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        bargap=0.3, # gap between bars of adjacent location coordinates.
        bargroupgap=0.1 # gap between bars of the same location coordinate.
        
        
    )
    
    for year in years:
            if math.isnan(df_fertility2_reporting[(df_fertility2_reporting['GEO']==country) & (df_fertility2_reporting['TIME']==year)]['Value']):
                fig.add_annotation(text="No data available", xref="x", x=year, y=0.5, yref="paper", textangle=70, showarrow=False)
    
    return fig

#### MIGRATION TAB CALLBACKS


@app.callback(
    Output('migration-lines', 'figure'),
    [Input('country_drop_migration_lines', 'value')]
)

def update_immigration_1(country):
    
    time.sleep(1)
    df_test = inm_preprocessing(df_immigration,country)
    
    
    
    x = df_test['TIME'].unique()
    x = np.sort(x)
    
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x = x, y = df_test[df_test['C_BIRTH'] == 'Reporting country']['Value'],
        mode='lines',
        line=dict(width=1, color='#F4be6f'),
        stackgroup='one',
        groupnorm='percent',# sets the normalization for the sum of the stackgroup
        name = 'Reporting Country'
    ))

    fig.add_trace(go.Scatter(
        x = x, y = df_test[df_test['C_BIRTH'] == 'Foreign country']['Value'],
        mode='lines',
        line=dict(width=1, color='#b0d7ac'),
        stackgroup='one',
        name = 'Foreign Country'
    ))


    fig.update_layout(
        #height = 500,
        #width = 1000,
        showlegend=True,
        xaxis_type='category',
        yaxis=dict(
            type='linear',
            range=[1, 100],
            ticksuffix='%'),
        
        plot_bgcolor='rgba(0,0,0,0)')
        

    return fig

@app.callback(
    Output('migration-bars', 'figure'),
    [Input('bars-button','n_clicks')],
    [State('country_drop_migration_bars', 'value'),
     State('stacked-bars','value'),
     State('radio-bars','value'),
     ]
)

def update_immigration_bars(n_clicks,country_list,stack,absolute):
    
    time.sleep(2)
    
    i=0
    for country in country_list:
        if i==0:
            df_test = inm_preprocessing(df_immigration,country).reset_index(drop=True)
        else:
            df_test = pd.concat([df_test,inm_preprocessing(df_immigration,country).reset_index(drop=True)])
        i+=1
    
    df_test = df_test[df_test['TIME']==2019]
    
    df_test_reporting = df_test[df_test['C_BIRTH']=='Reporting country'].reset_index(drop=True)
    df_test_foreign = df_test[df_test['C_BIRTH']=='Foreign country'].reset_index(drop=True)
    
    if absolute == 'Absolute':
        fig=go.Figure(data=[

            go.Bar(name = 'Reporting country', x=country_list, y=[df_test_reporting[df_test_reporting['GEO']==country]['Value'].iloc[0] for country in country_list], marker_color='#F4be6f'),
            go.Bar(name = 'Foreign country', x=country_list, y=[df_test_foreign[df_test_foreign['GEO']==country]['Value'].iloc[0] for country in country_list], marker_color='#b0d7ac')

        ])
        
        if stack==['Stack']:
            fig.update_layout(barmode='stack')
    
    if absolute == 'Percentages':
        
        df_test_total_value = df_test_reporting['Value'].reset_index(drop=True)+df_test_foreign['Value'].reset_index(drop=True)
        df_test_reporting['Value'] = (df_test_reporting['Value']/df_test_total_value)*100
        df_test_foreign['Value'] = (df_test_foreign['Value']/df_test_total_value)*100
        
        fig = go.Figure(
            data=[

            go.Bar(name = 'Reporting country', x=country_list, y=[df_test_reporting[df_test_reporting['GEO']==country]['Value'].iloc[0] for country in country_list], marker_color='#F4be6f'),
            go.Bar(name = 'Foreign country', x=country_list, y=[df_test_foreign[df_test_foreign['GEO']==country]['Value'].iloc[0] for country in country_list],  marker_color='#b0d7ac')

        ]
        )
        
        if stack==['Stack']:
            fig.update_layout(barmode='stack')
        
        fig.update_layout(yaxis=dict(
            type='linear',
            ticksuffix='%')
                         )
    fig.update_layout(
                             
                             plot_bgcolor='rgba(0,0,0,0)',
                             xaxis = dict(
                                          title = 'Native/Foreign Population Distribution in 2019',
                                          title_font_family='Glacial Indifference',
                                          title_font_color='#002B6B',
                                          title_font_size = 17,
                                          ))
        
    return fig


#### POP PYRAMIDS TAB CALLBACKS
    
@app.callback(
    Output('pop_pyramid1', 'figure'),
    [Input('country_drop1', 'value'),
     Input('year_slider', 'value')]
)

def update_graph1(country, year):
    
    time.sleep(1)
    df_test = preprocess_poppyramid(df_pyramids,country,year)
    
    y_age = df_test['new_age_ranges']
    x_M = df_test['Males']
    x_F = df_test['Females'] * -1

    ################################################### xticks automatic adjustment #####################################################################################
    m = np.array(df_test['Males'])
    f = np.array(df_test['Females'] * -1)
    all_ = np.concatenate([m,f])

    mini = round(np.min(all_),0)
    maxi = round(np.max(all_),0)

    minil = len(str(np.abs(mini)))

    def human_format(num):
        num = float('{:.3g}'.format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

    if minil == 3:
        mini = round(mini,-2)
        maxi = round(maxi,-2)
        step = 100
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]
    
    if minil == 4:
        mini = round(mini,-3)
        maxi = round(maxi,-3)
        step = 1000
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]

    if minil == 5:
        mini = round(mini,-4)
        maxi = round(maxi,-4)
        step = 10000
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]

    if minil == 6:
        mini = round(mini,-5)
        maxi = round(maxi,-5)
        step = 100000
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]

    if minil == 7:
        mini = round(mini,-6)
        maxi = round(maxi,-6)
        step = 1000000
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]

    if minil == 8:
        mini = round(mini,-7)
        maxi = round(maxi,-7)
        step = 10000000
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]

    ########################################################################################################################################
    
    if np.sum(x_M) == 0:
        y_age = [0]
        x_M = [0]
        x_F = [0]
        nx = [0]
        xticksls = [0]
        fig = go.Figure()
        fig.add_annotation(text="No data available for the selected year",
                  x=0.5,y=0.5, xref="paper", yref="paper", showarrow=False,
                  font=dict(
                    
                    size=16,
                    
                    ))
        
        fig.update_layout(                        
                             plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgba(0,0,0,0)',
                                                          
                             )
        fig.update_xaxes(showgrid=False, zeroline=False, showticklabels = False)
        fig.update_yaxes(showgrid=False, zeroline= False, showticklabels = False)
        
    else:
        # Creating instance of the figures
        fig = go.Figure()
          
        # Adding Male data to the figure
        fig.add_trace(go.Bar(y= y_age, x = x_M, 
                             name = 'Male', 
                             orientation = 'h',
                              marker={'color' : '#6facf4'}))
          
        # Adding Female data to the figure
        fig.add_trace(go.Bar(y = y_age, x = x_F,
                             name = 'Female', orientation = 'h',
                             marker={'color' : '#F4be6f'}))
        
        
        
            # Updating the layout for our graph
        fig.update_layout(title = 'Population Pyramid of ' + str(country),
                             title_font_size = 20, barmode = 'relative', title_font_family='Glacial Indifference', title_font_color='#002B6B',
                             bargap = 0.0, bargroupgap = 0, plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgba(0,0,0,0)',
                             xaxis = dict(tickvals = nx,
                                            
                                          ticktext = xticksls,
                                          
                                          title = 'Population',
                                          title_font_family='Glacial Indifference',
                                          title_font_size = 17,
                                          ))
    return fig

   
@app.callback(
    Output('pop_pyramid2', 'figure'),
    [Input('country_drop2', 'value'),
     Input('year_slider', 'value')]
)

def update_graph2(country, year):
    
    time.sleep(1)
    df_test = preprocess_poppyramid(df_pyramids,country,year)
    
    y_age = df_test['new_age_ranges']
    x_M = df_test['Males']
    x_F = df_test['Females'] * -1

    ################################################### xticks automatic adjustment #####################################################################################
    m = np.array(df_test['Males'])
    f = np.array(df_test['Females'] * -1)
    all_ = np.concatenate([m,f])

    mini = round(np.min(all_),0)
    maxi = round(np.max(all_),0)

    minil = len(str(np.abs(mini)))

    def human_format(num):
        num = float('{:.3g}'.format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

    if minil == 3:
        mini = round(mini,-2)
        maxi = round(maxi,-2)
        step = 100
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]
    
    if minil == 4:
        mini = round(mini,-3)
        maxi = round(maxi,-3)
        step = 1000
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]

    if minil == 5:
        mini = round(mini,-4)
        maxi = round(maxi,-4)
        step = 10000
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]

    if minil == 6:
        mini = round(mini,-5)
        maxi = round(maxi,-5)
        step = 100000
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]

    if minil == 7:
        mini = round(mini,-6)
        maxi = round(maxi,-6)
        step = 1000000
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]

    if minil == 8:
        mini = round(mini,-7)
        maxi = round(maxi,-7)
        step = 10000000
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]

    ########################################################################################################################################
    
    if np.sum(x_M) == 0:
        y_age = [0]
        x_M = [0]
        x_F = [0]
        nx = [0]
        xticksls = [0]
        fig = go.Figure()
        fig.add_annotation(text="No data available for the selected year",
                  x=0.5,y=0.5, xref="paper", yref="paper", showarrow=False,
                  font=dict(
                    
                    size=16,
                    
                    ))
        
        fig.update_layout(                        
                             plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgba(0,0,0,0)',
                                                          
                             )
        fig.update_xaxes(showgrid=False, zeroline=False, showticklabels = False)
        fig.update_yaxes(showgrid=False, zeroline= False, showticklabels = False)
        
    else:
        # Creating instance of the figures
        fig = go.Figure()
          
        # Adding Male data to the figure
        fig.add_trace(go.Bar(y= y_age, x = x_M, 
                             name = 'Male', 
                             orientation = 'h',
                              marker={'color' : '#6facf4'}))
          
        # Adding Female data to the figure
        fig.add_trace(go.Bar(y = y_age, x = x_F,
                             name = 'Female', orientation = 'h',
                             marker={'color' : '#F4be6f'}))
        
        
        
            # Updating the layout for our graph
        fig.update_layout(title = 'Population Pyramid of ' + str(country),
                             title_font_size = 20, barmode = 'relative', title_font_family='Glacial Indifference', title_font_color='#002B6B',
                             bargap = 0.0, bargroupgap = 0, plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgba(0,0,0,0)',
                             xaxis = dict(tickvals = nx,
                                            
                                          ticktext = xticksls,
                                          
                                          title = 'Population',
                                          title_font_family='Glacial Indifference',
                                          title_font_size = 17,
                                          ))
    return fig

   
@app.callback(
    Output('pop_pyramid3', 'figure'),
    [Input('country_drop3', 'value'),
     Input('year_slider', 'value')]
)

def update_graph3(country, year):
    
    time.sleep(1)
    df_test = preprocess_poppyramid(df_pyramids,country,year)
    
    y_age = df_test['new_age_ranges']
    x_M = df_test['Males']
    x_F = df_test['Females'] * -1

    ################################################### xticks automatic adjustment #####################################################################################
    m = np.array(df_test['Males'])
    f = np.array(df_test['Females'] * -1)
    all_ = np.concatenate([m,f])

    mini = round(np.min(all_),0)
    maxi = round(np.max(all_),0)

    minil = len(str(np.abs(mini)))

    def human_format(num):
        num = float('{:.3g}'.format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

    if minil == 3:
        mini = round(mini,-2)
        maxi = round(maxi,-2)
        step = 100
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]
    
    if minil == 4:
        mini = round(mini,-3)
        maxi = round(maxi,-3)
        step = 1000
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]

    if minil == 5:
        mini = round(mini,-4)
        maxi = round(maxi,-4)
        step = 10000
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]

    if minil == 6:
        mini = round(mini,-5)
        maxi = round(maxi,-5)
        step = 100000
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]

    if minil == 7:
        mini = round(mini,-6)
        maxi = round(maxi,-6)
        step = 1000000
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]

    if minil == 8:
        mini = round(mini,-7)
        maxi = round(maxi,-7)
        step = 10000000
        nx = list(range(mini,maxi+step,step))
        
        l1 = list(range(mini,0,step))
        l1 = [ -x for x in l1]
        l1 = [human_format(i) for i in l1]
        
        l2 = list(range(0+step,maxi+step,step))
        l2 = [human_format(i) for i in l2]
        
        xticksl = l1+[0]+l2
        xticksls = [ str(i) for i in xticksl]

    ########################################################################################################################################
    
    if np.sum(x_M) == 0:
        y_age = [0]
        x_M = [0]
        x_F = [0]
        nx = [0]
        xticksls = [0]
        fig = go.Figure()
        fig.add_annotation(text="No data available for the selected year",
                  x=0.5,y=0.5, xref="paper", yref="paper", showarrow=False,
                  font=dict(
                    
                    size=16,
                    
                    ))
        
        fig.update_layout(                        
                             plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgba(0,0,0,0)',
                                                          
                             )
        fig.update_xaxes(showgrid=False, zeroline=False, showticklabels = False)
        fig.update_yaxes(showgrid=False, zeroline= False, showticklabels = False)
        
    else:
        # Creating instance of the figures
        fig = go.Figure()
          
        # Adding Male data to the figure
        fig.add_trace(go.Bar(y= y_age, x = x_M, 
                             name = 'Male', 
                             orientation = 'h',
                              marker={'color' : '#6facf4'}))
          
        # Adding Female data to the figure
        fig.add_trace(go.Bar(y = y_age, x = x_F,
                             name = 'Female', orientation = 'h',
                             marker={'color' : '#F4be6f'}))
        
        
        
            # Updating the layout for our graph
        fig.update_layout(title = 'Population Pyramid of ' + str(country),
                             title_font_size = 20, barmode = 'relative', title_font_family='Glacial Indifference', title_font_color='#002B6B',
                             bargap = 0.0, bargroupgap = 0, plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgba(0,0,0,0)',
                             xaxis = dict(tickvals = nx,
                                            
                                          ticktext = xticksls,
                                          
                                          title = 'Population',
                                          title_font_family='Glacial Indifference',
                                          title_font_size = 17,
                                          ))
    return fig

# @app.callback(Output('tab1content', 'children'),
#                Input('tabs', 'value'))

# def loadingtab1(value):
#      time.sleep(2)
#      raise PreventUpdate

# @app.callback(Output('tab2content', 'children'),
#                Input('tabs', 'value'))

# def loadingtab2(value):
#      time.sleep(2)
#      raise PreventUpdate
    
# @app.callback(Output('tab3content', 'children'),
#                Input('tabs', 'value'))

# def loadingtab3(value):
#      time.sleep(2)
#      raise PreventUpdate
    
# @app.callback(Output('tab4content', 'children'),
#                Input('tabs', 'value'))

# def loadingtab4(value):
#      time.sleep(2)
#      raise PreventUpdate

# @app.callback(Output('tab5content', 'children'),
#               Input('tabs', 'value'))

# def loadingtab5(value):
#      time.sleep(2)
#      raise PreventUpdate


if __name__ == '__main__':
    app.run_server(debug=True)
            