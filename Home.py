import streamlit as st
st.set_page_config(
    page_title="OLX V3 KPIs",
    #page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

import pandas as pd
from datetime import date, timedelta
import plotly.express as px
import numpy as np
from io import StringIO
from dateutil.relativedelta import relativedelta
import openpyxl

"""
# Inspirel 
## Pregled prodaje po mjesecima
"""

#Global variables
ignore_sheets = ['Bonus 2023','Izgubljena prodaja Dorzol','Cumulative Dorzol','Bonus 2022','Weekly sales','Cumulative']


def get_sheets(file, ignore_sheets):
    sheets = []

    # Load the Excel workbook
    workbook = openpyxl.load_workbook(file)

    # Get all sheet names
    sheet_names = workbook.sheetnames

    # Print all sheet names
    for sheet_name in sheet_names:
        if sheet_name in ignore_sheets:
            pass
        else:
            sheets.append(sheet_name)
    
    return sheets

def get_data(file, sheet):
    df = pd.read_excel('data.xlsx', sheet_name=sheet)
    
    #Drop empty rows
    df.dropna(subset=['Artikal'], inplace=True)
    
    # Extract values in the 'Artikal' column where other columns are NaN
    new_column_values = df['Artikal'].where(df.drop(columns='Artikal').isnull().all(axis=1))

    # Forward fill the extracted values
    new_column_values.ffill(inplace=True)

    # Add the new column to the DataFrame
    df['Regija'] = new_column_values
    
    #Drop empty rows
    df.dropna(subset=['Datum'], inplace=True)
    
    return df

sheets = get_sheets('data.xlsx', ignore_sheets)

df1 = get_data('data.xlsx', sheets[0])

for sheet in sheets[1:]:
    df = get_data('data.xlsx', sheet)
    df1 = pd.concat([df, df1], axis=0)

df1.to_csv('Inspirel_consolidated.csv')

st.write(df1)
