import streamlit as st
import json
import random
import pandas as pd

import plotly.graph_objects as go
from welly import Project
from pathlib import Path

import helper2

base_dir = "./data/McMurray_data"
fpath = Path(base_dir+"/las/*.LAS")
p = Project.from_las(str(fpath))


#get the first well. this need to be updated with the well list
df = p[0].df()

def app():
    st.title('Correlation Panel')
    st.write('well logs displayed below')



# first argument takes the titleof the selectionbox
# second argument takes options

    f = open('/home/user/github_repo/t21-hack-SwellCorr/log_dict.json',)

    log_inp = json.load(f)

    ls1 = log_inp['log1-1']
    ls2 = log_inp['log2-1']
    ls3 = log_inp['log2-2']

    log1 = go.Scatter(x=df[ls1].values.tolist(), y=df.index, name=ls1)
    log2 = go.Scatter(x=df[ls2].values.tolist(), y=df.index, xaxis='x2', name=ls2)
    try:
        log3 = go.Scatter(x=df[ls3].values.tolist(), y=df.index, xaxis='x2', name=ls3)
    except:
        log3 = go.Scatter(x=[0], y=[0], xaxis='x2', name='empty')

    data = [log1, log2, log3]
    meta = ['logtrace1', 'logtrace2', 'logtrace3']

    layout = go.Layout(
        xaxis=dict(
            domain=[0,0.45],
            range=[0,150],
            position=1
        ),
        xaxis2=dict(
            domain=[0.55,1],
            range=[-1,6],
            type='log',
            position=1
        ),
        hovermode="y",
        height=800,
        template="plotly_white",
        
        
        
    )
    #fig = go.Figure(data=data, layout=layout)
    '''
    meta = ["My Figure 1", "Data"]
    t = [1,2,3]
    u = [3,2,1]
    data = [go.Scatter(x=t, 
                  y=t, 
                  mode='lines',
                  meta=meta),
            go.Scatter(x=t, 
                  y=u, 
                  mode='lines',
                  meta=meta)
    ]
    layout = {'title': '%{data[0].meta[0]}' }
     '''     
    
   
    fig = go.Figure(data=data, layout=layout)

    st.plotly_chart(fig, use_container_width=True)


def ranseries(n):
    randomlist = random.sample(range(1,n), 50)
    return pd.Series(randomlist)    



    