import streamlit as st
st.set_page_config(
    page_title="Inspirehl",
    #page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

import pandas as pd
from datetime import date, timedelta, datetime
import plotly.express as px
import numpy as np
from io import StringIO
from dateutil.relativedelta import relativedelta
import openpyxl
import plotly.graph_objects as go

import gdown



def update_podataka():
    st.write('Update podataka pokrenut.')
    url = "https://drive.google.com/drive/folders/1DjdfdT4yF9NAWaZgw4n7oVHGe_hCKnEk"
    file = gdown.download_folder(url, quiet=True, use_cookies=False)
    st.write('File preuzet')
    fajl = file[0]

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
        df = pd.read_excel(fajl, sheet_name=sheet)

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

    sheets = get_sheets(fajl, ignore_sheets)

    df1 = get_data('Promet JGL OFT sedmicni 2024.xlsx', sheets[0])

    for sheet in sheets[1:]:
        df = get_data('Promet JGL OFT sedmicni 2024.xlsx', sheet)
        df1 = pd.concat([df, df1], axis=0)
        df1.dropna(how='all', axis=1, inplace=True) 

    df1.to_csv('Inspirel_consolidated.csv')
    st.write('Update gotov.')

with st.sidebar:
    if st.button('Osvježi podatke'):
        update_podataka()


"""
# Inspirehl
"""


df = pd.read_csv('Inspirel_consolidated.csv')

df['Datum'] = df['Datum'].str.replace(" ","")
df['Datum'] = pd.to_datetime(df['Datum'], format='mixed', dayfirst=True)


#Napraviti Entitet polje

def set_color(row):
    if row["Regija"] == "11 - Brčko Distrikt":
        return "BD"
    elif row["Regija"] == "12 - RS":
        return "RS"
    else:
        return "FBiH"

df = df.assign(Entitet=df.apply(set_color, axis=1))

df['Year'] = df['Datum'].dt.year 
df['Month'] = df['Datum'].dt.month 
df['Short_title'] = df['Artikal'].str.split(' ').str[0]
df['Regija'] = df['Regija'].str.title()


#Filteri

#col1, col2, col3 = st.columns(3)
col1, col2 = st.columns([2,1])
prvi_datum = datetime(2022, 1, 1).date()

yesterday_date = date.today() - timedelta(1)

with st.sidebar:
    #if st.button('Osvježi podatke'):
        #update_podataka()

    #selected_date = st.slider(
        #"Izaberi period",
        #min_value=prvi_datum,
        #max_value=yesterday_date,
        #value=(prvi_datum, yesterday_date),
        #step=timedelta(days=1),
    #)

    #Datum opcije
    #Ovaj mjesec
    #Prošli mjesec
    #Tekuća godina
    #Od 2022. godine

    datum_periodi = st.selectbox(
        "Izaberi neki od predefinisanih perioda",
        ("Od 2022. godine", "Tekuća godina", "Prošli mjesec", "Tekući mjesec"))

    if datum_periodi == "Od 2022. godine":
        dd = datetime(2022, 1, 1).date()
        dd2 = yesterday_date
    elif datum_periodi == "Tekuća godina":
        dd = datetime(2024, 1, 1).date()
        dd2 = yesterday_date
    elif datum_periodi == "Prošli mjesec":
        dd = yesterday_date.replace(day=1) - relativedelta(months=1)
        dd2 = yesterday_date.replace(day=1) - relativedelta(days=1)
    elif datum_periodi == "Tekući mjesec":
        dd = yesterday_date.replace(day=1)
        dd2 = yesterday_date

    d = st.date_input("Unesi ili izaberi početni datum", dd)
    d2 = st.date_input("Unesi ili izaberi krajnji datum", dd2)
    
    lijekovi = df['Short_title'].unique()
    artikli = st.multiselect("Izaberi lijekove",options=lijekovi, default=lijekovi)

    entitet = st.multiselect("Izaberi Entitet", options=('FBiH','RS','BD'), default=('FBiH','RS','BD'))
    
    kantoni = df.Regija.unique()
    kanton = st.multiselect("Izaberi Kanton/Regiju", options=kantoni, default=kantoni)

    poslovni_partneri = df['Poslovni partner'].unique()
    poslovni_partner = st.selectbox(label='Izaberi poslovnog partnera',options=poslovni_partneri, index=None)

#with col3:
    #poredjenje = st.selectbox("Izaberi poređenje: ",("Prethodni period (MoM)","Prethodna godina (YoY)"),index=1)

color_map_artikli={
    "Dorzol": "#636EFA",
    "Glaumax": "#EF553B",
    "Latanox": "#00CC96",
    "Bimanox": "#AB63FA",
    "Moksacin": "#FFA15A"}

color_map_entiteti={
    "FBiH": "#636EFA",
    "RS": "#EF553B",
    "BD": "#00CC96"}
    



#d = selected_date[0]
#d2 = selected_date[1]

dana = (d2 - d)


# if poredjenje == "Prethodna godina (YoY)":
#     momd = d - relativedelta(years=1)
#     momd2 = d2 - relativedelta(years=1)
#     ppp = " YoY"
# else:
#     momd = d - timedelta(dana.days)
#     momd2 = d2 - timedelta(dana.days)
#     ppp = " MoM"

df1 = df.query('Datum >= "'+str(d)+'" & Datum <= "'+str(d2)+'"')


if len(entitet) > 0:
    ddd = []
    for c in entitet:
        ddd.append(c)
    df1 = df1[df1['Entitet'].isin(ddd)]

if len(kanton) > 0:
    ddd = []
    for c in kanton:
        ddd.append(c)
    df1 = df1[df1['Regija'].isin(ddd)]


if len(artikli) > 0:
    dddd = []
    for c in artikli:
        dddd.append(c)
    df1 = df1[df1['Short_title'].isin(dddd)]

if poslovni_partner:
    df1 = df1[df1['Poslovni partner'] == str(poslovni_partner)]

#st.write(df1)

df1 = df1.drop_duplicates()

def total_artikal(artikal):
    art = df1.query('Short_title == "'+str(artikal)+'"')
    art = art['Količina'].sum()
    art = int(float(art))
    return art

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    art = 'Dorzol'
    st.metric(label=art,value=f"{total_artikal(art):,}",delta=None)
with col2:
    art = 'Glaumax'
    st.metric(label=art,value=f"{total_artikal(art):,}",delta=None)
with col3:
    art = 'Latanox'
    st.metric(label=art,value=f"{total_artikal(art):,}",delta=None)
with col4:
    art = 'Bimanox'
    st.metric(label=art,value=f"{total_artikal(art):,}",delta=None)
with col5:
    art = 'Moksacin'
    st.metric(label=art,value=f"{total_artikal(art):,}",delta=None)



#check_graph = df1.groupby('Datum')['Količina'].sum().reset_index()
#fig = px.line(check_graph, x='Datum', y='Količina')
#st.plotly_chart(fig, use_container_width=True, config=dict(
    #displayModeBar=False))

col1, col2 = st.columns([3,1])
with col1:
    """
    ### Pregled prodaje po mjesecima
    """
    #Ostvarena prodaja po mjesecu
    by_month = df1.groupby(['Year','Month'])['Količina'].sum().reset_index()
    #fig = px.bar(by_month, x=['Year','Month'], y='Količina', color='Year', text_auto=True)
    by_region_product = by_month.sort_values(by=['Year','Month'])
    by_region_product2 = by_month.pivot(index=['Month'],columns='Year',values='Količina').fillna(0).reset_index()
    by_region_product = pd.melt(by_region_product2,
    id_vars=['Month'],
    value_vars=None,
    var_name=None,
    value_name='Količina',
    col_level=None,
    ignore_index=True)

    fig = px.bar(by_region_product, x='Month',y='Količina', text_auto=True, facet_col='Year')
    fig.update_layout(dragmode=False)
    fig.update_layout(yaxis_title=None)
    fig.update_layout(xaxis_title=None)
    fig.update_xaxes(type='category')
    fig.update_xaxes(nticks=12) 
    #fig.update_traces(textposition='inside')
    st.plotly_chart(fig, use_container_width=True, config=dict(
        displayModeBar=False))

with col2:
    """
    ### Omjer prodaje po artiklu
    """
    #Omjer prodaje po artikli
    by_product = df1.groupby(['Short_title'])['Količina'].sum().reset_index()

    fig = px.pie(by_product, values='Količina',names='Short_title', color='Short_title', color_discrete_map=color_map_artikli)
    fig.update_layout(dragmode=False)
    fig.update_layout(yaxis_title=None)
    fig.update_layout(xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True, config=dict(
            displayModeBar=False))


col1, col2 = st.columns([3,1])
with col1:
    """
    ### Pregled prodaje po Entitetu/Regiji
    """
    #Ostvarena prodaja po regionu
    by_region = df1.groupby(['Entitet','Regija'])['Količina'].sum().reset_index()
    by_region = by_region.sort_values(by=['Količina'], ascending=False)
    fig = px.bar(by_region, x='Regija', y='Količina', color='Entitet', text_auto=True, color_discrete_map=color_map_entiteti)
    fig.update_layout(dragmode=False)
    fig.update_layout(yaxis_title=None)
    fig.update_layout(xaxis_title=None)
    fig.update_xaxes(type='category')
    #fig.update_xaxes(nticks=12) 
    #fig.update_traces(textposition='inside')
    st.plotly_chart(fig, use_container_width=True, config=dict(
        displayModeBar=False))

with col2:
    """
    ### Omjer prodaje po regionu
    """
    #Omjer prodaje po regionu
    by_entity = df1.groupby(['Entitet'])['Količina'].sum().reset_index()

    fig = px.pie(by_entity, values='Količina',names='Entitet', color='Entitet', color_discrete_map=color_map_entiteti)
    fig.update_layout(dragmode=False)
    fig.update_layout(yaxis_title=None)
    fig.update_layout(xaxis_title=None)
    st.plotly_chart(fig, use_container_width=True, config=dict(
            displayModeBar=False))


"""
### Ostvarena prodaja po mjesecu i artiklu
"""
#Ostvarena prodaja po mjesecu i artiklu
by_month_product = df1.groupby(['Year','Month','Short_title'])['Količina'].sum().reset_index()
by_month_product["Period"] = by_month_product["Year"].astype(str) +"/" + by_month_product["Month"].astype(str)
by_month_product = by_month_product.sort_values(by=['Year','Month','Short_title'], ascending=True).reset_index(drop=True)
#by_month_product = by_month_product[['Period','Short_title','Količina']]
#fig = px.bar(by_month_product, x='Period', y='Količina', color='Artikal', text_auto=True)
by_month_product2 = by_month_product.pivot(index=['Year','Month','Period'],columns='Short_title',values='Količina').fillna(0).reset_index()
by_month_product = pd.melt(by_month_product2,
    id_vars=['Year','Month','Period'],
    value_vars=None,
    var_name=None,
    value_name='Količina',
    col_level=None,
    ignore_index=True)
fig = px.line(by_month_product, x='Period', y='Količina', color='Short_title', color_discrete_map=color_map_artikli, markers=True)
fig.update_layout(dragmode=False)
fig.update_layout(yaxis_title=None)
fig.update_layout(xaxis_title=None)
fig.update_traces(mode='markers+lines',line=dict(width=3))
#fig.update_xaxes(type='category')
#fig.update_xaxes(nticks=12)
#fig.update_traces(textposition='inside')
st.plotly_chart(fig, use_container_width=True, config=dict(
    displayModeBar=False))

by_month_product_pivot = by_month_product.pivot(index='Short_title', columns='Period', values='Količina')
by_month_product_pivot = by_month_product_pivot.sort_values(by=['Short_title'])
st.write(by_month_product_pivot)

"""
### Ostvarena kumulativna prodaja po regionu i artiklu
"""
#Ostvarena prodaja po regionu i artiklu
by_region_product = df1.groupby(['Entitet','Regija','Short_title'])['Količina'].sum().reset_index()
by_region_product = by_region_product.sort_values(by=['Regija'])
by_region_product2 = by_region_product.pivot(index=['Entitet','Regija'],columns='Short_title',values='Količina').fillna(0).reset_index()
by_region_product = pd.melt(by_region_product2,
    id_vars=['Entitet','Regija'],
    value_vars=None,
    var_name=None,
    value_name='Količina',
    col_level=None,
    ignore_index=True)
by_region_product = by_region_product.sort_values(by=['Količina'], ascending=False)
fig = px.bar(by_region_product, x='Regija', y='Količina', color='Short_title', text_auto=True, color_discrete_map=color_map_artikli)
fig.update_layout(dragmode=False)
fig.update_layout(yaxis_title=None)
fig.update_layout(xaxis_title=None)
fig.update_xaxes(type='category')
#fig.update_xaxes(nticks=12) 
#fig.update_traces(textposition='inside')
st.plotly_chart(fig, use_container_width=True, config=dict(
    displayModeBar=False))


by_region_product_pivot = by_region_product.pivot(index=['Entitet','Regija'], columns='Short_title', values='Količina')
by_region_product_pivot = by_region_product_pivot.sort_values(by=['Regija'])
st.write(by_region_product_pivot)

"""
### Ostvarena kumulativna prodaja po regionu i artiklu - drugi prikaz
"""

by_region_product = df1.groupby(['Entitet','Regija','Short_title'])['Količina'].sum().reset_index()
artikala = by_region_product['Short_title'].unique()

def zadnji_graph(by_region_product, x):
        by_region_product = by_region_product.query("Short_title == '"+str(x)+"'")
        by_region_product = by_region_product.sort_values(by=['Količina'], ascending=False).reset_index()
        fig = px.bar(by_region_product, x='Regija', y='Količina', color='Short_title', text_auto=True, color_discrete_map=color_map_artikli,title=str(x))
        fig.update_layout(dragmode=False)
        fig.update_layout(yaxis_title=None)
        fig.update_layout(xaxis_title=None)
        fig.update_xaxes(type='category')
        fig.update_traces(showlegend=False) 
        #fig.update_xaxes(nticks=12) 
        #fig.update_traces(textposition='inside')
        st.plotly_chart(fig, use_container_width=True, config=dict(
            displayModeBar=False))

        tabela = by_region_product[['Regija','Short_title','Količina']]
        st.write(tabela)
if len(artikala) == 1:
    zadnji_graph(by_region_product,artikala[0])
        
elif len(artikala) == 2:
    col1, col2 = st.columns(2)
    with col1:
        zadnji_graph(by_region_product,artikala[0])
        
    with col2:
        zadnji_graph(by_region_product,artikala[1])
        
else:
    def assign_columns(values):
        # Initialize dictionaries to count occurrences of each column value
        col_counts = {'col1': 0, 'col2': 0, 'col3': 0}

        # Iterate over the list of values
        for value in values:
            # Find the column with the fewest occurrences
            min_col = min(col_counts, key=col_counts.get)
            # Assign the value to that column
            col_counts[min_col] += 1
            yield min_col, value

    values = artikala

    kolone = []
    # Assign columns to values
    for col, value in assign_columns(values):
        kolone.append([col,value])

    koldf = pd.DataFrame(kolone, columns=['Kolona','Ime'])

    col1, col2, col3 = st.columns(3)

    with col1:
        iterdata = koldf[koldf['Kolona']=='col1']
        for index, row in iterdata.iterrows():
            zadnji_graph(by_region_product,row['Ime'])

    with col2:
        iterdata = koldf[koldf['Kolona']=='col2']
        for index, row in iterdata.iterrows():
            zadnji_graph(by_region_product,row['Ime'])

    with col3:
        iterdata = koldf[koldf['Kolona']=='col3']
        for index, row in iterdata.iterrows():
            zadnji_graph(by_region_product,row['Ime'])


