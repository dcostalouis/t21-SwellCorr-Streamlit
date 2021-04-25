import app1
import app2
import streamlit as st
import helper2
from welly import Project
from pathlib import Path
import pickle

PAGES = {
    "Well Panel": app1,
    "Template": app2
}

well_uwi = helper2.well_list()
well_uwi = st.sidebar.selectbox("Well Names", well_uwi) #need to add the well filter to filter logs by well

st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
page = PAGES[selection]
page.app()

base_dir = "./data/McMurray_data"
fpath = Path(base_dir+"/las/*.LAS")
p = Project.from_las(str(fpath))


loglist = helper2.curve_list()
with open("loglist.txt", "wb") as fp:
    pickle.dump(loglist, fp)

with open("welllist.txt", "wb") as fp:
    pickle.dump(well_uwi, fp)
