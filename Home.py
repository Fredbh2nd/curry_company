import streamlit as st
from PIL import Image

st.set_page_config(
    page_title = 'Home',
    page_icon = "💻️"
)

# image_path = '/home/fred/'
image = Image.open( 'projeto_logo.png' )
st.sidebar.image( image, width=120 )

st.header('Marketplace - Visão Empresa')

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write( '# Curry Company Growth Dashboard' )

st.markdown(
    ''''
    Growth Dashboard foi construíd opara acompanhar as métricas de crescimento dos Entregadores e Restaurante.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        -Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insinghts de geolocalição.
    - Visão Entregador:
        - Acompanhar dos indicadores semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento de restaurantes
    ### Ask for Help
    - Time de Data Science do Discord
        -@meigarom
    ''')
    
        