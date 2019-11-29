import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
import dash_table

df = pd.read_csv('aggr.csv', parse_dates=['Entry time'])
params = list(df)
max_length = len(df)

## Model
def filter_df(df,exchange, margin, start_date,end_date): #función para filtrar los datos
    #recibe excahnge, inicio el margen y la fecha de incio y la filtra
    filtered_df=df[(df['Exchange']==exchange) & (df['Margin']==margin) & (df['Entry time']>=start_date) & (df['Entry time']<=end_date)]
    
    return filtered_df

def generate_section_banner(title):
    return html.Div(className="section-banner", children=title)
## Layout

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/uditagarwal/pen/oNvwKNP.css', 'https://codepen.io/uditagarwal/pen/YzKbqyV.css'])

app.layout = html.Div(children=[
    html.Div(
            children=[
                html.H2(children="Bitcoin Leveraged Trading Backtest Analysis", className='h2-title'),
            ],
            className='study-browser-banner row'
    ),
    html.Div(
        className="row app-body",
        children=[
            html.Div(
                className="twelve columns card",
                children=[
                    html.Div(
                        className="padding row",
                        children=[
                            html.Div(
                                className="two columns card",
                                children=[
                                    html.H6("Select Exchange",),
                                    dcc.RadioItems(
                                        id="exchange-select",
                                        options=[
                                            {'label': label, 'value': label} for label in df['Exchange'].unique()
                                        ],
                                        value='Bitmex',
                                        labelStyle={'display': 'inline-block'}
                                    )
                                ]
                            ),
                            html.Div(
                                className="two columns card",
                                children=[
                                    html.H6("Select Leverage",),
                                    dcc.RadioItems(
                                        id="leverage-select",
                                        options=[
                                            {'label': label, 'value': label} for label in df['Margin'].unique()
                                        ],
                                        value=1,
                                        labelStyle={'display': 'inline-block'}
                                    )
                                ]
                            ),
                            html.Div(
                                className="three columns card",
                                children=[
                                    html.H6("Select a Date Range"),
                                            dcc.DatePickerRange(
                                                id="date-range-select",
                                                start_date=df['Entry time'].min(),
                                                end_date=df['Entry time'].max(),
                                                display_format='MMM YY'
                                            )
                                ]
                            ),
                            
                        ]
                )
        ]),
        html.Div(
                className="padding row",
                children=[
                    html.Div(
                        className="six columns card",
                        children=[
                            dash_table.DataTable(
                                id='table',
                                columns=[
                                    {'name': 'Number', 'id': 'Number'},
                                    {'name': 'Trade type', 'id': 'Trade type'},
                                    {'name': 'Exposure', 'id': 'Exposure'},
                                    {'name': 'Entry balance', 'id': 'Entry balance'},
                                    {'name': 'Exit balance', 'id': 'Exit balance'},
                                    {'name': 'Pnl (incl fees)', 'id': 'Pnl (incl fees)'},
                                ],
                                style_cell={'width': '50px'},
                                style_table={
                                    'maxHeight': '450px',
                                    'overflowY': 'scroll'
                                },
                            )
                        ]
                    ),
                    dcc.Graph(#grafo
                        id="pnl-types",
                        className="six columns card",
                        figure={}
                    )
                ]
            ),
        html.Div(
                className="padding row",
                children=[
                    dcc.Graph(
                        id="daily-btc",
                        className="six columns card",
                        figure={}
                    ),
                    dcc.Graph(
                        id="balance",
                        className="six columns card",
                        figure={}
                    )
                ]
            ),
            html.Div([
                dcc.Graph(
                    id="piechart",
                    figure={}
                )   
            ]

            ),
            html.Div([
                dcc.Graph(
                    id="barChart",
                    figure={}
                )
            ]),
            html.Div([
                dcc.Graph(
                    id="barChart3",
                    figure={}
                )
            ]),
            html.Div([
               dcc.Graph(
                   id="Scatter",
                   figure={}
               ) 
            ])
            
            
            
    ])        
])

#Controller
@app.callback(
    [dash.dependencies.Output(component_id='date-range-select', component_property='start_date'),
     dash.dependencies.Output(component_id='date-range-select', component_property='end_date')],
    [
        dash.dependencies.Input(component_id='exchange-select', component_property='value')
    ]
)
def update_date_exchange(value):
    t=df[df['Exchange']==value]['Entry time'].apply(lambda x: x.strftime('%Y-%m-%d'))
    start_date = t.min()
    end_date = t.max()
    return [start_date,end_date]

@app.callback(
    dash.dependencies.Output('table', 'data'),
    (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date'),
    )
)
def update_table(exchange, leverage, start_date, end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    return dff.to_dict('records')


@app.callback(
    dash.dependencies.Output('pnl-types', 'figure'),
    (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date'),
    )
)
def update_barchart(exchange,leverage, start_date,end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    trace1 = go.Bar(x=dff[dff['Trade type']=='Long']['Entry time'], y=dff[dff['Trade type']=='Long']['Pnl (incl fees)'], name='Long', )
    trace2 = go.Bar(x=dff[dff['Trade type']=='Short']['Entry time'], y=dff[dff['Trade type']=='Short']['Pnl (incl fees)'], name='Short', )
    
    
    return {
        'data': [trace1, trace2],
        'layout': go.Layout(title='Pnl vs Trade type',
                            colorway=["#EF963B", "#EF533B"], hovermode="closest")}

@app.callback(
    dash.dependencies.Output('daily-btc', 'figure'),
    (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date'),
    )
)
def update_dailybtc(exchange,leverage, start_date,end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    trace=go.Scatter(x=dff["Entry time"], y=dff['BTC Price'], name='BTC Price', mode='lines',
                                marker={'size': 8, "opacity": 0.6, "line": {'width': 0.5}}, )
    return {"data": [trace],
            "layout": go.Layout(title="Daily BTC Price", xaxis={"title": "Date"})}

@app.callback(
    dash.dependencies.Output('balance', 'figure'),
    (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date'),
    )
)
def update_balance(exchange,leverage, start_date,end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    trace=go.Scatter(x=dff["Entry time"], y=dff['Entry balance'], name='Balance', mode='lines',
                                marker={'size': 8, "opacity": 0.6, "line": {'width': 0.5}}, )
    return {"data": [trace],
            "layout": go.Layout(title="Balance overtime", xaxis={"title": "Date"})}

@app.callback(
    dash.dependencies.Output('piechart', 'figure'),
    (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date'),
    )
)
def update_piechart(exchange,leverage, start_date,end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    label = dff['Trade type'] 
    values = len(dff[dff['Trade type']=='Long']),len(dff[dff['Trade type']=='Short'])
    
    graf = go.Pie(labels = label, values = values,hoverinfo='label+percent',textinfo='value')
    return{
        "data":[graf],
        "layout": go.Layout(title="Pie Chart (Shor And Long)")

    }



@app.callback(
    dash.dependencies.Output('barChart', 'figure'),
    (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date'),
    )
)

def update_barchart(exchange,leverage, start_date,end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    
    trace3 =  go.Bar(x=dff[dff['Trade type']=='Long']['Entry time'], y=dff[dff['Trade type']=='Long']['Pnl (incl fees)'], name='Long', )
    return {
        'data': [trace3],
        'layout': go.Layout(title='barChart Long',
                            colorway=["#EF963B", "#EF533B"], hovermode="closest")}    



@app.callback(
    dash.dependencies.Output('barChart3', 'figure'),
    (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date'),
    )
)
   
def update_barchart(exchange,leverage, start_date,end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    trace4 = go.Bar(x=dff[dff['Trade type']=='Short']['Entry time'], y=dff[dff['Trade type']=='Short']['Pnl (incl fees)'], name='Short', )
    
    return {
        'data': [trace4],
        'layout': go.Layout(title='barChart Short',
                            colorway=["#EF963B", "#EF533B"], hovermode="closest")}    



@app.callback(
    dash.dependencies.Output('Scatter', 'figure'),
    (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range-select', 'start_date'),
        dash.dependencies.Input('date-range-select', 'end_date'),
    )
)

def update_Scatter(exchange,leverage, start_date,end_date):
    
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    trace5=go.Scatter(x=dff["Pnl (incl fees)"], y=dff['Profit'], mode='markers',
                                marker={'size': 8, "opacity": 0.6, "line": {'width': 0.5}}, )
    
    return {"data": [trace5],
            "layout": go.Layout(title="Scatter Chart  Pnl (incl fees)")
        }



if __name__ == "__main__":
    app.run_server(debug=True)
