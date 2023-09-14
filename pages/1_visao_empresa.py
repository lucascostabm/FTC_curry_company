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

df = pd.read_csv('dataset/train.csv')
st.set_page_config(page_title= 'Visão empresa', layout= 'wide')


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
#                     VISÃO EMPRESA
# ======================================================

# Agrupamento e contagem:

df_q1 = df1.loc[:, ['Order_Date', 'ID']].groupby(['Order_Date']).count().reset_index()  # Tenho que resetar o index, para que meu dataframe esteja completo, para que todas as colunas sejam mantidas e não transformadas em index.
px.bar(df_q1, x = 'Order_Date', y = 'ID')

# ======================================================
#               BARRA LATERAL
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
#               LAYOUT NO STREAMLIT
# ======================================================

st.header('Marketplace - Visão Cliente')
tab1, tab2, tab3 = st.tabs(['Visão gerencial', 'Visão tática', "Visão geográfica"])

with tab1:
    with st.container():
        st.markdown("# Visão Gerencial")

        df_q1 = df1.loc[:, ['Order_Date', 'ID']].groupby(['Order_Date']).count().reset_index()  # Tenho que resetar o index, para que meu dataframe esteja completo, para que todas as colunas sejam mantidas e não transformadas em index.
        fig = px.bar(df_q1, x = 'Order_Date', y = 'ID', title= 'Orders by date')
        st.plotly_chart(fig, use_container_width= True, )
    
    with st.container():
        col1, col2 = st.columns (2)
        with col1:
            df_q3 = df1.loc[:, ['ID', 'Road_traffic_density']].groupby( 'Road_traffic_density' ).count().reset_index()
            df_q3 = df_q3.loc[df_q3['Road_traffic_density'] != 'NaN ', :]
            df_q3['%'] = df_q3['ID'] / df_q3['ID'].sum() * 100

            fig = px.pie(df_q3, names = 'Road_traffic_density', values = '%', title= 'Traffic order share')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            df_q4 = df1.loc[((df1['City'] != 'NaN ') & (df1['Road_traffic_density'] != 'NaN ')), ['ID', 'City', 'Road_traffic_density']].groupby( ['City', 'Road_traffic_density']).count().reset_index()

            fig = px.scatter( df_q4, y= 'City', x = 'Road_traffic_density', size = 'ID', color = 'City', title= 'Traffic order city')
            st.plotly_chart(fig, use_container_width=True)

with tab2: 
    with st.container():
        df1['week_year'] = df1['Order_Date'].dt.strftime( '%U' )  # A mascara '%U' retorna a semana do ano (começando domingo) e %W (semana começando segunda)
        df_q2 = df1.loc[:, ['week_year', 'ID']].groupby( ['week_year'] ).count().reset_index()

        fig = px.line(df_q2, x = 'week_year', y = 'ID', title= 'Order share by week')
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        df_q5 = df1.loc[:, ['ID', 'week_year']].groupby('week_year').count().reset_index()
        df_q5_1 = df1.loc[:, ['Delivery_person_ID', 'week_year']].groupby('week_year').nunique().reset_index()
        dfq5 = pd.merge(df_q5, df_q5_1, how = 'inner')
        dfq5['Order_by_deliver'] = dfq5['ID'] / dfq5['Delivery_person_ID']

        fig = px.line(dfq5, x = 'week_year', y = 'Order_by_deliver', title= 'Unique delivery person')
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    df_q6 = df1.loc[:, ['City', 'Road_traffic_density', 'ID', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    map = folium.Map()
    for index, location in df_q6.iterrows():
        folium.Marker( [location['Delivery_location_latitude'],
                    location['Delivery_location_longitude']],
                    popup = location[['City', 'Road_traffic_density']]).add_to( map )
    folium_static (map, width = 860, height = 600)
