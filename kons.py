#Import Libraries
import streamlit as st
import pandas as pd
import geojson
import folium
from streamlit_folium import folium_static
import numpy as np
import plotly_express as px
########################################################################
# Conservation Map of Indonesia
# Developed by Rayhan Fakhriza Mardana Putra
# Courtesy of Project Sakti
########################################################################

# Header Setting
st.set_page_config(page_title='Animal Conservation Map',  layout='wide', page_icon=':tiger:')

st.image('logops.png', width=200)
st.title('Peta Habitat Satwa Dilindungi di Indonesia')
st.markdown('Developed by Project Sakti')
st.divider()


# Insight Satwa
st.header('Satwa Dilindungi Dalam Angka')

col1,col2,col3 = st.columns(3)
col1.metric(label="Jumlah Kelas Satwa", value=9)
col2.metric(label="Jumlah Famili Satwa", value=131)
col3.metric(label="Jumlah Spesies",value=787)

pie1,pie2,pie3 = st.columns(3)

with pie2:
    kelas_pie = pd.read_excel('2-dash.xlsx',sheet_name='Kelas',index_col=False) # Dataframe
    fig = px.pie(kelas_pie, values='Jumlah Spesies', names='Kelas')
    fig.update_traces(textinfo='value')
    st.plotly_chart(fig, use_container_width=True)

st.header('Pilih dan Kenali Satwa Dilindungi')

# Peta Habitat

main = pd.read_excel('2-dash.xlsx',sheet_name='Data',index_col=False) # Dataframe

# Searchbox
#species_cari = st.text_input('Cari Nama Spesies:')

# Filter data based on species name entered in the search box
#filtered_data = main[main['Nama Spesies'].str.contains(species_cari, case=False, na=False)]

# Selectbox Layout
col1, col2, col3 = st.columns(3)

kls = col1.selectbox('Pilih Kelas Satwa', main['Kelas'].unique())
jen_option = main[main['Kelas']== kls]['Jenis'].unique()
jen = col2.selectbox('Pilih Jenis Satwa',jen_option)
sps_option = main[main['Jenis']== jen]['Nama Spesies'].unique()
sps = col3.selectbox('Pilih Spesies',sps_option)

filtered_data = main[(main['Kelas'] == kls) & 
                     (main['Jenis'] == jen) & 
                     (main['Nama Spesies'] == sps)]

# Create Map
with open("nkri_fix.geojson", "r") as f:
    geojson_data = geojson.load(f)

# Layout of the Map and Description

col1,col2 = st.columns(2, gap="large")

with col1:
    m = folium.Map(tiles="cartodb positron",
                location=[-2.49607,117.89587],
                zoom_start=4)

    # Add GeoJSON layer to the map
    tooltip = folium.GeoJsonTooltip(
        fields=["Provinsi Habitat"],
        aliases=["Province:"],
        localize=True,
        sticky=False,
        labels=True,
        style="""
            background-color: #F0EFEF;
            border: 2px solid black;
            border-radius: 3px;
            box-shadow: 3px;
        """,
    )

    folium.GeoJson(geojson_data,
                style_function=lambda x: {'fillColor': '#FFFFFF', 
                                            'color': 'black', 
                                            'weight': 0.5, 
                                            'fillOpacity': 0}).add_to(m)

    # Highlight provinces from filtered data
    for feature in geojson_data['features']:
        province_name = feature['properties']['Provinsi Habitat']
        if province_name in filtered_data['Provinsi Habitat'].values:
            folium.GeoJson(feature,
                        style_function=lambda x: {'fillColor': '#008000', 
                                                            'color': 'black', 
                                                            'weight': 0, 
                                                            'fillOpacity': 0.5}).add_to(m)
        else:
            folium.GeoJson(feature,
                        style_function=lambda x: {'fillColor': '#FFFFFF', 
                                                            'color': 'black', 
                                                            'weight': 0, 
                                                            'fillOpacity': 0}).add_to(m)

    folium_static(m)

# Display the Fact of the Animal

binom = filtered_data.iloc[0, 1]
species = filtered_data.iloc[0,2]
family = filtered_data.iloc[0,4]
cat = filtered_data.iloc[0,6]
desc = filtered_data.iloc[0,7]
prov_list = filtered_data['Provinsi Habitat']
prov = prov_list.reset_index(drop=True)
prov.index = np.arange(1, len(prov) + 1)

with col2:
    fact = st.container(border=True)
    fact.header(f"{species}")
    fact.divider()
    fact.markdown(f'**Nama Ilmiah** : *{binom}*')
    fact.markdown(f'**Famili** : {family}')
    fact.markdown('**Kategori IUCN** :')
    
    # Condition for IUCN Category
    if cat == "CR":
        fact.subheader(f':red[{cat}]')
        fact.markdown(f':red[**{desc}**]')
    elif cat == "EN":
        fact.subheader(f':orange[{cat}]')
        fact.markdown(f':orange[**{desc}**]')
    elif cat == "VU":
        fact.subheader(f':blue[{cat}]')
        fact.markdown(f':blue[**{desc}**]')
    elif cat == "NT":
        fact.subheader(f':green[{cat}]')
        fact.markdown(f':green[**{desc}**]')
    elif cat == "LC":
        fact.subheader(f':green[{cat}]')
        fact.markdown(f':green[**{desc}**]')
    else:
        fact.subheader(f'{cat}')
        fact.markdown(f'{desc}')
    
    fact.write(prov)
