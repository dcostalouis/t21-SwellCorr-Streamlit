from welly import Project
from pathlib import Path

def load_wells():
    base_dir = "./data/McMurray_data"

    # # load well data
    """Need to add a method for the user to point to the directory or add additional las files later"""
    fpath = Path(base_dir+"/las/*.LAS")
    return Project.from_las(str(fpath))

def well_list():
    return [w.uwi for w in load_wells()]

def curve_list():
    df = load_wells()[0].df() ##gets data from the first well in the Welly Project
    return df.columns.tolist()

