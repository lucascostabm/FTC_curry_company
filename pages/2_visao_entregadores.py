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
st.set_page_config(page_title= 'Visão entregadores', layout= 'wide')


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

st.header('Marketplace - Entregadores')
tab1, tab2, tab3 = st.tabs(["Visão gerencial", '-', '-'])

with tab1: 
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='Large')
        with col1:
            # Menor idade
            max_age = list(df1.loc[:, ['Delivery_person_Age', 'Delivery_person_ID']].max())
            col1.metric('Maior idade: ', max_age[0])
            st.markdown(f'###### Entregador: {max_age[1]}')

        with col2:
            # Maior idade
            min_age = list(df1.loc[:, ['Delivery_person_Age', 'Delivery_person_ID']].min())
            col2.metric('Menor idade', min_age[0])
            st.markdown(f'###### Entregador: {min_age[1]}')

        with col3:
            vei_more = list(df1.loc[:, ['Vehicle_condition', 'Delivery_person_ID']].max())
            col3.metric(f'Melhor veículo:', vei_more[0])
            st.markdown(f'###### Entregador: {vei_more[1]}')

        with col4:
            vei_less = list(df1.loc[:, ['Vehicle_condition', 'Delivery_person_ID']].min())
            col4.metric('Pior veículo: ', vei_less[0])
            st.markdown(f'###### Entregador: {vei_less[1]}')
    
    with st.container():
        st.markdown("""---""")
        st.title('Ratings')

        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### Avaliação média por entregador')
            dfe_q3 = (df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']].
                      groupby(['Delivery_person_ID'])
                      .mean()
                      )
            st.dataframe(dfe_q3,use_container_width= True)

        with col2:
            st.markdown('###### Avaliação média por tipo de tráfego')
            df_q4 = df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings': ['mean','std']})
            df_q4.columns = ['Delivery_mean', 'Delivery_std']
            df_q4.reset_index()
            st.dataframe(df_q4, use_container_width= True)

            st.markdown('###### Avaliação média por condição climática')
            df_q5 = df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings': ['mean','std']})
            df_q5.columns = ['Delivery_mean', 'Delivery_std']
            df_q5.reset_index()
            st.dataframe(df_q5, use_container_width= True)
    
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('###### Entregadores mais rápidos')
            df_q6 = df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby( ['City', 'Delivery_person_ID']).min().sort_values( ['City', 'Time_taken(min)'])
            df_q6['Time_taken(min)'] = df_q6['Time_taken(min)'].str.split(' ').str[1]
            df_q6_top10 = df_q6.groupby('City').head(10)
            st.dataframe(df_q6_top10, use_container_width= True)

        with col2:
            st.markdown('###### Entregadores mais lentos')
            df_q6 = df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby( ['City', 'Delivery_person_ID']).min().sort_values( ['City', 'Time_taken(min)'])
            df_q6['Time_taken(min)'] = df_q6['Time_taken(min)'].str.split(' ').str[1]
            df_q6_top10 = df_q6.groupby('City').tail(10)
            st.dataframe(df_q6_top10, use_container_width= True)
        
