from welly import Well, Project # Welly is used to organize the well data and project collection
from striplog import Legend, Striplog, StriplogError
import plotly.express as px # plotly is used as the main display functionality
import matplotlib.pyplot as plt 

from dash import Dash, callback_context # dash is used to update the plot and fields dynamically in a web browser
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import flask
from glob import glob

import json
import numpy as np
import pandas as pd
from pathlib import Path
import numpy as np
import base64
import os

import helper


def get_curves(p):
    """
    Gets a list of curves from the wells in the project
    """
    curve_list = []
    for well in p:
        curves = well.data.keys()
        for c in curves:
            curve_list.append(c)
    return sorted(set(curve_list))


def get_tops_df(project, tops_field='tops', columns=['UWI', 'PICK', 'MD']):
    """
    Returns a DataFrame of tops from a welly Project
    """
    tops_set = []
    rows = []
    for well in project:
        for t in well.data[tops_field]:
            row = [well.uwi, t.components[0]['formation'], t.top.middle]
            tops_set.append(t.components[0]['formation'])
            rows.append(row)
    df = pd.DataFrame(rows, columns=columns)
    return df


def make_well_project(laspath='data/las/', stripath='data/tops/'):
    """
    Return a dictionary of wells and striplogs where the
    key is the base filename
    """
    wells = {}
    lasfiles = glob(laspath + '*.LAS')
    stripfiles = glob(stripath + '*.csv')
    for fname, sname in zip(lasfiles, stripfiles):
        name = fname.split('/')[-1].split('.')[0]
        wells[name] = Well.from_las(fname)
        wells[name].data['tops'] = Striplog.from_csv(sname)
        proj = Project(list(wells.values()))
    return proj


def section_plot(p, legend=None, ymin=3000, ymax=5500):
    fig = plt.figure(constrained_layout=True, figsize=(6,10))
    axes_names = [name.replace(' ','-') for name in p.uwis]
    ax_dict = fig.subplot_mosaic([axes_names])
    for i, w in enumerate(p):
        name = w.uwi.replace(' ','-')
        w.data['tops'].plot(ax=ax_dict[w.uwi.replace(' ','-')], legend=legend, alpha=0.5)
        plot_tops(ax_dict[name], w.data['tops'], field='formation', ymin=ymin, ymax=ymax)
        ax_dict[name].plot(w.data['GR']/120, w.data['GR'].basis, c='k', lw=0.5)
        ax_dict[name].set_xlim(0,175/120)
        ax_dict[name].set_ylim(ymax, ymin)
        ax_dict[name].set_title(name)
        if i != 0:
            ax_dict[name].set_yticklabels([])

    fig.savefig('cross_section.png')
    return 


def plot_tops(ax, striplog, ymin=0, ymax=1e6, legend=None, field=None, **kwargs):
    """
    Plotting, but only for tops (as opposed to intervals).
    """
    if field is None:
        raise StriplogError('You must provide a field to plot.')

    ys = [iv.top.z for iv in striplog]

    try:
        try:
            ts = [getattr(iv.primary, field) for iv in striplog]
        except:
            ts = [iv.data.get(field) for iv in striplog]
    except:
        print('Could not find field')
        #raise StriplogError('Could not retrieve field.')

    for y, t in zip(ys, ts):
        if (y > ymin) and (y < ymax):
            ax.axhline(y, color='lightblue', lw=3, zorder=0)
            ax.text(0.1, y,#-max(ys)/200, 
                    t, fontsize=10, ha='left', va='center', bbox=dict(facecolor='white', 
                                                         edgecolor='grey', 
                                                         boxstyle='round',
                                                         alpha=0.75))
    return


def get_first_curve(curve_list):
    if 'GR' in curve_list:
        curve = 'GR'
    else:
        curve = curve_list[0] ## gets the first curve name for the plotly figure
    return curve


def df_to_csvtxt(df, out_fields = ['top', 'Comp formation']):
    """
    This take a DataFram (df) for a well, and converts it into
    as csv-like string to make a Striplog
    """ 
    header = 'top, Comp formation\n'
    csv_txt = ''
    csv_txt += csv_txt + header
    for i, row in df.iterrows():
        csv_txt = csv_txt + str(row['MD']) + ', ' + row['PICK'] + '\n'
    return csv_txt


app = Dash(__name__)
# Create server variable with Flask server object for use with gunicorn
server = app.server


# Get las files
path = 'data/Poseidon_data/las/'
print('\n LAS PATH:', path, '\n')
lasfiles = glob(path + '*.LAS')
for fname in lasfiles:
    print(' '*5, fname)
print('\n')


# Get striplog files
path2 = 'data/Poseidon_data/tops/'
print('\n STRIP PATH:', path2, '\n')
stripfiles = glob(path2 + '*.csv')
for fname in stripfiles:
    print(' '*5, fname)
print('\n')

tops_legend = Legend.from_csv(filename='data/Poseidon_data/tops_legend.csv')

p = Project.from_las('data/Poseidon_data/las/*.LAS')
well_uwi = [w.uwi for w in p] ##gets the well uwi data for use in the well-selector tool

# Add striplogs to Project
# Striplog must have the same name as LAS file.
# e.g. Torosa-1.LAS and Torosa-1.csv
for w in p:
    name = Path(w.fname).name.split('.')[0]
    new_path = f'data/Poseidon_data/tops/{name}.csv'
    print(name, new_path)
    strip = Striplog.from_csv(f'data/Poseidon_data/tops/{name}.csv')
    w.data['tops'] = strip


# Make the well correlation panel
def encode_xsection(p):
    """
    Takes the project and saves a xsec PNG a disk and encodes it for dash
    """
    section_plot(p, tops_legend)
    image_filename = 'cross_section.png' # replace with your own image 
    encoded_image = base64.b64encode(open(image_filename, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded_image.decode())


# Initialize Cross-section
# section_plot(p) # , tops_legend)
# image_filename = 'cross_section.png' # replace with your own image 
# encoded_image = base64.b64encode(open(image_filename, 'rb').read())


well = p[0]  ##gets data from the first well in the Welly Project
curve_list = get_curves(p) ##gets the column names for later use in the curve-selector tool
curve = get_first_curve(curve_list)
## Load well top data
#surface_picks_df = pd.read_table(Path('./well_picks/data/McMurray_data/PICKS.TXT'),
#                                usecols=['UWI', 'PICK', 'MD'])
surface_picks_df = get_tops_df(p)
print(surface_picks_df.info())

#well dropdown selector
well_dropdown_options = [{'label': k, 'value': k} for k in sorted(well_uwi)] ##list of wells to the dropdown
#tops dropdown options
"""we need to have a stratigraphic column at some point"""
tops_dropdown_options = [{'label': k, 'value': k} for k in list(surface_picks_df['PICK'].unique())] ##list of tops to the dropdown
##well log curve dropdown options
curve_dropdown_options = [{'label': k, 'value': k} for k in sorted(curve_list)] ##list of well log curves to the dropdown

# draw the initial plot
fig_well_1 = px.line(x=well.data[curve], y=well.data[curve].basis, labels = {'x':curve, 'y': 'MD'}) ##polot data and axis lables
fig_well_1.update_yaxes(autorange="reversed") ## flips the y-axis to increase down assuming depth increases
fig_well_1.layout.xaxis.fixedrange = True ##forces the x axis to a fixed range based on the curve data
fig_well_1.layout.template = 'plotly_white' ##template for the plotly figure

app.title = "SwellCorr"
app.layout = html.Div(children=[
    html.Div(
        children=[
            html.H4('SwellCorr well correlation')
        ]
    ),
    html.Div(
        children=[
            html.Div([
                'Select well:', ##Well selector
                dcc.Dropdown(id='well-selector', options=well_dropdown_options, value=p[0].uwi, style={'width': '200px'}),

                'Edit tops:', ##existing top to edit selector
                dcc.Dropdown(id='top-selector', options=tops_dropdown_options, placeholder="Select a top to edit", style={'width': '200px'}),
                
                html.Hr(),
                'Create a new surface pick:', html.Br(), ##dialog to creat a new well top correlation for a well
                dcc.Input(id='new-top-name', placeholder='Name for new top', type='text', value=''),
                html.Button('Create', id='new-top-button'),
                
                html.Hr(),
                'Curve Select:', html.Br(), ##well log curve selector
                dcc.Dropdown(id='curve-selector', options=curve_dropdown_options, value=curve, placeholder="Select a curve", style={'width': '200px'}),
                
                html.Hr(),
                "Write tops to file:", ##input box and button for outputting well correlation results to file
                dcc.Input(id='input-save-path', type='text', placeholder='path_to_save_picks.json', value=''),
                html.Button('Save Tops', id='save-button', n_clicks=0),

                html.Hr(), ##button to update the Striplog dict on the page
                html.Button('Update Striplog', id='gen-striplog-button')

            ]),
            dcc.Graph(id="well_plot", 
                        figure=fig_well_1,
                        style={'width': '200', 'height':'1000px'}), ##figure of log curve with well tops

            html.Div([
                # hidden_div for storing tops data as json
                # Currently not hidden for debugging purposes. change style={'display': 'none'}
                html.Div(id='tops-storage', children=surface_picks_df.to_json()),#, style={'display': 'none'}),

                html.Hr(),
                html.H4('Striplog CSV Text:'),
                html.Pre(id='striplog-txt', children='', style={'white-space': 'pre-wrap'}),            
                #html.Img(id='corr-plot', src='data:image/png;base64,{}'.format(encoded_image)) #src='cross-section.png')
                html.Img(id='cross-section', src=encode_xsection(p)) #src='cross-section.png')
            ]),
            
            # hidden_div for storing un-needed output
            html.Div(id='placeholder', style={'display': 'none'})
        ],
        style={'display': 'flex'}
    ),
    html.Div(
        html.P(children=['The swell way of correlating wells'])
    )
    ]
)

@app.callback(
    Output('cross-section', 'src'),
    [Input('tops-storage', 'children')],
    [State('well-selector', 'value')])
def update_cross_section(tops_storage, well_uwi):
    """
    top_storage_json to striplogs to project. 
    to return encoded str (image)
    """
    wells_tops = pd.read_json(tops_storage)
    well_tops = wells_tops[wells_tops.UWI == well_uwi]
    csv_txt = df_to_csvtxt(well_tops)
    p.get_well(well_uwi).data['tops'] = Striplog.from_csv(text=csv_txt)
    return encode_xsection(p)


@app.callback(
    [Output('curve-selector', 'options'),
     Output('curve-selector', 'value')],
    [Input('well-selector', 'value')])
def well_update_changes_curves(well_uwi):  
    """
    def for updating curve list and curves
    """
    w = p.get_well(well_uwi)  # identifies and gets the correct welly.Well object based on well_uwi
    curve_list = sorted(list(w.data))
    curve = get_first_curve(curve_list)
    curve_dropdown_options = [{'label': k, 'value': k} for k in curve_list]  #creates dropdown list
    return curve_dropdown_options, curve  # returns the dropdown list options and the initial curve


# update tops data when graph is clicked or new top is added
@app.callback(
    Output('tops-storage', 'children'),
    [Input('well_plot', 'clickData'),
     Input('new-top-button', 'n_clicks')],
    [State("top-selector", "value"),
     State("tops-storage", "children"),
     State('new-top-name', 'value'),
     State('well-selector', 'value'),
     State('top-selector', 'options')])
def update_pick_storage(clickData, new_top_n_clicks, active_pick, surface_picks, new_top_name, active_well, tops_options):
    """Update the json stored in tops-storage div based on y-value of click"""
    
    # Each element in the app can only be updated by one call back function.
    # So anytime we want to change the tops-storage it has to be inside of this function.
    # We need to use the dash.callback_context to determine which event triggered
    # the callback and determine which actions to take
    # https://dash.plotly.com/advanced-callbacks    
    surface_picks_df = pd.read_json(surface_picks)
    
    # get callback context
    ctx = callback_context
    if not ctx.triggered:
        event_elem_id = 'No clicks yet'
    else:
        event_elem_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # do the updating based on context
    if event_elem_id == "well_plot": # click was on the plot
        if active_pick:
            y = clickData['points'][0]['y']

            # update the tops depth df
            pick = {'UWI': active_well, 'PICK': active_pick, 'MD': y} 
            surface_picks_df = surface_picks_df.append(pick, ignore_index=True).drop_duplicates(subset=['UWI', 'PICK'], keep='last')
    
    if event_elem_id == "new-top-button": # click was on the new top button
        options = [d['value'] for d in tops_options] # tops_options is list of dicts eg [{'label': pick, 'value': pick}]
        if not new_top_name in options:
            pick = {'UWI': active_well, 'PICK': new_top_name, 'MD': np.nan} 
            surface_picks_df = surface_picks_df.append(pick, ignore_index=True).drop_duplicates(subset=['UWI', 'PICK'], keep='last')

    return surface_picks_df.to_json() 

# Update graph when tops storage changes
@app.callback(
    Output("well_plot", "figure"),
    [Input('tops-storage', 'children'),
     Input('curve-selector', 'value')],
     [State('well-selector', 'value')] ## With multiple wells the state of the well_uwi must be passed to select the right welly.Well
    )
def update_figure(picks, curve, active_well):
    """redraw the plot when the data in tops-storage is updated"""  
    w = p.get_well(active_well) ##selects the correct welly.Well object
    
    picks_df = pd.read_json(picks)
    picks_selected = picks_df[picks_df['UWI'] == active_well.replace(' ', '-')]
    
    # regenerate figure with the new horizontal line
    fig = px.line(x=w.data[curve], y=w.data[curve].basis, labels = {'x':curve, 'y': 'MD'})

    fig.layout = {'uirevision': curve} # https://community.plotly.com/t/preserving-ui-state-like-zoom-in-dcc-graph-with-uirevision-with-dash/15793
    fig.update_yaxes(autorange="reversed")
    fig.layout.xaxis.fixedrange = True
    fig.layout.template = 'plotly_white'
    helper.update_picks_on_plot(fig, picks_selected)
    
    return fig


# update dropdown options when new pick is created
@app.callback(
    Output("top-selector", "options"),
    [Input('tops-storage', 'children')])
def update_dropdown_options(surface_picks):
    """update the options available in the dropdown when a new top is added"""
    surface_picks = pd.read_json(surface_picks)
    tops_dropdown_options = [{'label': k, 'value': k} for k in list(surface_picks['PICK'].unique())]
    return tops_dropdown_options


# Write tops to external file
@app.callback(
    Output('placeholder', 'children'),
    [Input('save-button', 'n_clicks')],
    [State('tops-storage', 'children'),
    State('input-save-path', 'value')])
def save_picks(n_clicks, surface_picks, path):
    """
    Save out picks to a json file. 
    TODO: I am sure there are better ways to handle saving out picks, but this is proof of concept
    """
    #picks_df = pd.read_json(surface_picks)

    if path:
        path_to_save = Path('.') / 'well_picks' / 'data' / 'updates' / path
        with open(path_to_save, 'w') as f:
            json.dump(surface_picks, fp=f)

    return

# create striplog csv text
@app.callback(
    Output('striplog-txt', 'children'),
    [Input('gen-striplog-button', 'n_clicks'),
    Input('well-selector', 'value')],
    [State('tops-storage', 'children')])
def generate_striplog(n_clicks, active_well, surface_picks):
    print(active_well)
    surface_picks = pd.read_json(surface_picks)
    surface_picks = surface_picks[surface_picks['UWI'] == active_well]   
    s = helper.surface_pick_to_striplog(surface_picks)
    return json.dumps(s)

if __name__ == "__main__":
    app.run_server(port=4545, debug=True)