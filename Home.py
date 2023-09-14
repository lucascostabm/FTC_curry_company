import streamlit as st
from PIL import Image

st.set_page_config(
    page_title = "Home",
)

image_path = 'logo.png'
image = Image.open( image_path )
st.sidebar.image(image, width = 120)

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('##### Fastest delivery in town')
st.sidebar.markdown('''---''')

st.write ( '# Curry company Growth Dashboard')

st.markdown(
    '''
    Growth dashboard foi construido para acompanhar as métricas de crescimento dos entregadores e restaurantes
    ### Como utilizar esse dashboard?

    - Visão empresa: 
        - Visão gerencial: Métricas gerais de comportamento
        - Visão tática: Indicadores semanais de crescimento
        - Visão geográfica: Insights de geolocalização
    - Visão entregadores: 
        - Acompanhamento dos indicadores semanais de crescimento
    - Visão restaurantes:
        - Indicadores semanais de crescimento dos restaurantes
    
    ### Ask for help
    - lucascostabm@gmail.com
''')
