# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(id='site-dropdown',
                 options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                         [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                    min=0, max=10000, step=1000,
                    marks={i: str(i) for i in range(0, 10001, 2000)},
                    value=[min_payload, max_payload]),
    html.Br(),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
    html.Br(),

    # EXTRA: Bar chart for launch success rate by site
    html.Div(dcc.Graph(id='success-rate-bar-chart')),
    html.Br(),

    # EXTRA: Bar chart for payload range success rate
    html.Div(dcc.Graph(id='payload-success-bar')),
    html.Br(),

    # EXTRA: Bar chart for booster version success rate
    html.Div(dcc.Graph(id='booster-success-bar'))
])

# TASK 2: Callback for pie chart
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        pie_data = spacex_df[spacex_df['class'] == 1]
        fig = px.pie(pie_data,
                     names='Launch Site',
                     title='Total Successful Launches by Site')
    else:
        site_data = spacex_df[spacex_df['Launch Site'] == entered_site]
        outcome_counts = site_data['class'].value_counts().rename({1: 'Success', 0: 'Failure'}).reset_index()
        outcome_counts.columns = ['class', 'count']
        fig = px.pie(outcome_counts,
                     values='count',
                     names='class',
                     title=f'Success vs Failure for site {entered_site}',
                     color='class',
                     color_discrete_map={'Success': 'green', 'Failure': 'red'})
    return fig

# TASK 4: Callback for scatter plot
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'),
               Input(component_id='payload-slider', component_property='value')])
def get_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class',
                     color='Booster Version Category',
                     title='Correlation between Payload and Success',
                     labels={'class': 'Launch Outcome'})
    return fig

# EXTRA: Callback for success rate by site
@app.callback(Output(component_id='success-rate-bar-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def render_success_rate_chart(selected_site):
    df = spacex_df.copy()
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    success_rate = df.groupby('Launch Site')['class'].mean().reset_index(name='Success Rate')
    fig = px.bar(success_rate, x='Launch Site', y='Success Rate',
                 title='Launch Success Rate by Site',
                 text_auto='.2f')
    return fig

# EXTRA: Callback for payload range success rate
@app.callback(Output(component_id='payload-success-bar', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def payload_success_rate_chart(selected_site):
    df = spacex_df.copy()
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    bins = [0, 2000, 4000, 6000, 8000, 10000]
    labels = ['0-2k', '2k-4k', '4k-6k', '6k-8k', '8k-10k']
    df['Payload Range'] = pd.cut(df['Payload Mass (kg)'], bins=bins, labels=labels)

    payload_rate = df.groupby('Payload Range')['class'].mean().reset_index(name='Success Rate')
    fig = px.bar(payload_rate, x='Payload Range', y='Success Rate',
                 title='Launch Success Rate by Payload Range',
                 text_auto='.2f')
    return fig

# EXTRA: Callback for booster version success rate
@app.callback(Output(component_id='booster-success-bar', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def booster_success_rate_chart(selected_site):
    df = spacex_df.copy()
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]

    booster_rate = df.groupby('Booster Version Category')['class'].mean().reset_index(name='Success Rate')
    fig = px.bar(booster_rate, x='Booster Version Category', y='Success Rate',
                 title='Launch Success Rate by Booster Version',
                 text_auto='.2f')
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
