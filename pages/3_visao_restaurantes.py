# ======================================================
#           BIBLIOTECAS E CARREGAMENTO DE DATASET
# ======================================================

import pandas as pd
import datetime as dt
import plotly.express as px
import folium
import haversine as hs
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import numpy as np


df = pd.read_csv('dataset/train.csv')

st.set_page_config(page_title= 'Visão restaurante', layout= 'wide')

# ======================================================
#               PRÉ-PROCESSAMENTO
# ======================================================


df1 = df.copy()
# Convertendo as colunas numéricas para int

# 1 - Coluna Delivery_person_Age
df2 = df1.copy()
df2 = df2['Delivery_person_Age'].unique()
# Até esse ponto, identifiquei que existe um dado não númerico nessa coluna.
df1 = df1.loc[(df1['Delivery_person_Age'] != 'NaN '), :]
df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
# Nesse ponto tratei a coluna de idade

# 2 - Coluna Delivery_person_Ratings para float
df2 = df1.copy()
df2['Delivery_person_Ratings'].unique()  # Nessa coluna tabém existe dados 'NaN '
df1 = df1.loc[(df2['Delivery_person_Ratings'] != 'NaN '), :]
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
# Nesse ponto tratei a coluna de ratings

# Coluna Order_date para datetime. Nesse caso, ela está como objeto.
df2 = df1.copy()
df2['Order_Date'].unique() # Descobri que não tem dado que não esteja formatado como data
df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format = '%d-%m-%Y')

# Verificação da coluna 'Vehicle_condition'.
df1['Vehicle_condition'].unique() # Coluna não tem dado 'NaN ' (nesse momento, onde já temos dados filtrados)

# Verificação da coluna multiple_deliveries
df1['multiple_deliveries'].unique()  # Essa coluna tem dado 'NaN '
df1 = df1.loc[(df1['multiple_deliveries'] != 'NaN '), :]
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

# Removendo espaço extra nos textos da coluna ID
# uma forma de utilizar, sem considerar a execução de um comando for, seria usando o loc. O loc me retorna uma série, e essa série pode receber comandos exclusivos de string, quanto utilizamos o método 'str'.

df1.loc[:,'ID'].str.strip()
df1.loc[:,'Type_of_order'].str.strip()
df1.loc[:,'Type_of_vehicle'].str.strip()
df1.loc[:,'City'].str.strip()
df1.loc[:,'Road_traffic_density'].str.strip()

# Retirando NaN do dataset
df1 = df1.loc[(df1['Road_traffic_density'] != 'NaN '), :]
df1 = df1.loc[(df1['Time_taken(min)'] != 'NaN'), :]
df1 = df1.loc[(df1['City'] != 'NaN '), :]
df1 = df1.loc[(df1['Festival'] != 'NaN '), :]


# ======================================================
#              BARRA LATERAL
# ======================================================

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width = 120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('##### Fastest delivery in town')
st.sidebar.markdown('''---''')

st.sidebar.markdown('### Selecione uma data limite:')
date_slide = st.sidebar.slider(
    'Até qual valor?',
    value = pd.datetime( 2022, 4, 6),
    min_value = pd.datetime( 2022, 2, 11),
    max_value = pd.datetime(2022, 4, 6),
    format = 'DD-MM-YYYY')

st.sidebar.markdown('''---''')

traffic_option = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['High ', 'Jam ', 'Low ', 'Medium '],
    default =  ['High ', 'Jam ', 'Low ', 'Medium ']
)

# Filtro de data
linhas = df1['Order_Date'] < date_slide
df1 = df1.loc[linhas, :]

# Filtro de trânsito
linhas = df1['Road_traffic_density'].isin(traffic_option)
df1 = df1.loc[linhas, :]


# ======================================================
#              LAYOUT NO STREAMLIT
# ======================================================

st.header('Marketplace - Visão Restaurantes')
tab1, tab2, tab3 = st.tabs( ['Visão gerencial', '-', '-'])

with tab1:
    with st.container():
        st.header('Ratings')

        col1,col2,col3,col4,col5,col6 = st.columns(6)

        with col1:
            df_r1 = list(df1.loc[:, ['Delivery_person_ID']].nunique())
            st.markdown('###### Qtde entregadores')
            col1.metric(label = '', value= df_r1[0])
        
        with col2:
            df_r2 = df1.loc[:, ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']].apply( lambda x: hs.haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),(x['Delivery_location_latitude'], x['Delivery_location_longitude'])) ,axis = 1).reset_index()
            dist1 = list(df_r2.mean())[1]       
            st.markdown('###### Média distância')
            col2.metric(label = '', value=round(dist1,2))

        with col3:
            df_r6 = df1.loc[:, ['Time_taken(min)', 'Festival']].reset_index()
            df_r6['Time_taken(min)'] = df_r6['Time_taken(min)'].str.split(' ').str[1]
            df_r6 = df_r6.loc[1:(len(df_r6) - 2), :]
            df_r6['Time_taken(min)'] = df_r6['Time_taken(min)'].astype(int)
            df_r6 = df_r6.loc[:,:].groupby( ['Festival'] ).agg({'Time_taken(min)': ['mean', 'std']})
            df_r6.columns = ['Tempo médio', 'Desvio padrão médio']
            df_r6.reset_index()
            time_mf = df_r6.iloc[1,0].copy()
            time_sf = df_r6.iloc[1,1].copy()
            time_ms = df_r6.iloc[0,0].copy()
            time_ss = df_r6.iloc[0,1].copy()
            st.markdown('###### Tempo durante festival (min)')
            col3.metric(label = '', value=round(time_mf,2))
        with col4:
            st.markdown('###### STD durante festival (min)')
            col4.metric(label = '', value=round(time_sf,2))
        with col5:
            st.markdown('###### Tempo sem festival (min)')
            col5.metric(label = '', value=round(time_ms,2))
        with col6:
            st.markdown('###### STD sem festival (min)')
            col6.metric(label = '', value=round(time_ss,2))

    with st.container():
        st.markdown('#### Tempo médio de entrega por tipo de cidade')
        df_r3 = df1.loc[:, ['Time_taken(min)', 'City']].reset_index()
        df_r3['Time_taken(min)'] = df_r3['Time_taken(min)'].str.split(' ').str[1]
        df_r3 = df_r3.loc[1:(len(df_r3) - 2), :]
        df_r3['Time_taken(min)'] = df_r3['Time_taken(min)'].astype(int)
        df_r3 = df_r3.loc[:,:].groupby( 'City' ).agg({'Time_taken(min)': ['mean', 'std']})
        df_r3.columns = ['Tempo médio', 'Desvio padrão médio']
        df_r3 = df_r3.reset_index()

        fig = px.bar(df_r3, x = 'City', y = 'Tempo médio', error_y= 'Desvio padrão médio')
        st.plotly_chart(fig, use_container_width= True, )

    with st.container():
        st.markdown('#### Tempo médio e desvio padrão de entrega por cidade e tipo de tráfego')
        df_r5 = df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].reset_index()
        df_r5['Time_taken(min)'] = df_r5['Time_taken(min)'].str.split(' ').str[1]
        df_r5 = df_r5.loc[1:(len(df_r5) - 2), :]
        df_r5['Time_taken(min)'] = df_r5['Time_taken(min)'].astype(int)
        df_r5 = df_r5.loc[:,:].groupby( ['City', 'Road_traffic_density'] ).agg({'Time_taken(min)': ['mean', 'std']})
        df_r5.columns = ['Tempo médio', 'Desvio padrão médio']
        df_r5 = df_r5.reset_index()
        
        fig = px.sunburst(df_r5, path=['City', 'Road_traffic_density'], values = 'Tempo médio', color = 'Desvio padrão médio', color_continuous_scale= 'RdBu', color_continuous_midpoint = np.average(df_r5['Desvio padrão médio']))
        st.plotly_chart(fig)
        
    with st.container():
        st.markdown('#### Tempo médio e Desvio padrão por cidade e tipo de pedido')
        df_r4 = df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order']].reset_index()
        df_r4['Time_taken(min)'] = df_r4['Time_taken(min)'].str.split(' ').str[1]
        df_r4 = df_r4.loc[1:(len(df_r4) - 2), :]
        df_r4['Time_taken(min)'] = df_r4['Time_taken(min)'].astype(int)
        df_r4 = df_r4.loc[:,:].groupby( ['City', 'Type_of_order'] ).agg({'Time_taken(min)': ['mean', 'std']})
        df_r4.columns = ['Tempo médio', 'Desvio padrão médio']
        df_r4.reset_index()

        st.dataframe(df_r4, use_container_width= True)
