import pandas as pd
import numpy as np
from pyxirr import xirr

def fetch_data():
    return None

def prepare_data(df):
    


def calculate_xirr(df, timeperiod):
    return xirr(df.tail(timeperiod))