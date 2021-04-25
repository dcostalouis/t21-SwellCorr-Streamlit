import streamlit as st
import json
import pandas as pd
import random
from welly import Project
from pathlib import Path
import pickle



def app():
    st.title('Template')
    st.write('Select logs below')

    with open("loglist.txt", "rb") as fp:
        loglist = pickle.load(fp)
    
    left_column, right_column = st.beta_columns(2)
    # You can use a column just like st.sidebar:
    with left_column:
        log1_1 = st.selectbox("log1-1: ", loglist, index=1)
                
    # Or even better, call Streamlit functions inside a "with" block:
    with right_column:
        log2_1 = st.selectbox("log2-1: ",
                     loglist, index=0)
        log2_2 = st.selectbox("log2-2: ",
                     loglist, index=2)

    logdict = {'log1-1': log1_1,
                'log2-1': log2_1,
                'log2-2': log2_2}

    
    log_json = json.dumps(logdict)
    f = open("log_dict.json","w")
    f.write(log_json)
    f.close()