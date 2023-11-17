
# Libraries
from haversine import haversine
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import pandas as pd
from PIL import Image
import folium
import numpy as np
import streamlit as st
from streamlit_folium import folium_static

st.set_page_config( page_title='Visão Empresa', page_icon='📊️', layout='wide' )


# ================================ 
# Funcoes
# ================================

def country_maps( df1 ):
    df_aux = ( df1.loc[:, ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']]
                  .groupby(['City', 'Road_traffic_density'])
                  .median().reset_index())
           
    map = folium.Map()
    
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']]).add_to( map )
        
    folium_static( map, width=600, height=400 )

    return None
        
        

def order_share_by_week( df1 ):
    df_aux1 = df1.loc[:, ['ID','week_of_year']].groupby(['week_of_year']).count().reset_index()
    df_aux2 = ( df1.loc[:, ['Delivery_person_ID','week_of_year']]
                   .groupby(['week_of_year'])
                   .nunique().reset_index() )

    df_aux = pd.merge(df_aux1, df_aux2, how='inner' )
    df_aux['Order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    
    fig = px.line( df_aux, x='week_of_year', y='Order_by_delivery')

    return fig
    

def order_by_week( df1 ):         
    df1['week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )

    df_aux = df1.loc[:, ['ID','week_of_year']].groupby(['week_of_year']).count().reset_index()
        
    fig = px.line(df_aux, x='week_of_year', y='ID')


    return fig


def traffic_order_city( df1 ):            
    df_aux = ( df1.loc[:, ['ID', 'City', 'Road_traffic_density'] ]
                  .groupby(['City','Road_traffic_density'])
                  .count().reset_index() )
           
    fig = px.scatter( df_aux, x='City', y='Road_traffic_density', size='ID', color='City' )

    return fig
    

def traffic_order_share( df1 ):            
    df_aux = ( df1.loc[:, ['ID', 'Road_traffic_density']]
                  .groupby(['Road_traffic_density'])
                  .count().reset_index() )
    
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    
    fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')

    return fig



def order_metric( df1 ):
    # Order Matric 
    cols = ['ID', 'Order_Date']
    # Selecao de linhas
    df_aux = df1.loc[:, cols].groupby(['Order_Date']).count().reset_index()
           
    # Desenhar o fráfico de linhas

    fig = px.bar(df_aux, x='Order_Date', y='ID')

    return fig


def clean_code( df1 ):
    """ Esta funcao tem a responsabilidade de limpar o dataframe
        Tipos de limpeza:
        1. Remocao dos dados NaN
        2. Mudanca do tipo da coluna de dados
        3. Remocao dos espacos das variaveis de texto
        4. FOrmatacao da coluna de datas 
        5. Limpeza da coluna de tempo ( remcao do texto da varial numerica)
        Input: Datafrme
        Output: Dataframe
    """
    
    # Excluir as linhas com a idade dos entregadores vazia
    linhas_vazias = df1[ 'Delivery_person_Age' ] != "NaN "
    df1 = df1.loc[ linhas_vazias, : ].copy()
    
    # Excluir as linhas com a idade dos entregadores vazia
    linhas_vazias = df1[ 'Road_traffic_density' ] != "NaN "
    df1 = df1.loc[ linhas_vazias, : ].copy()
    
    # Excluir as linhas com a idade dos entregadores vazia
    linhas_vazias = df1[ 'City' ] != "NaN "
    df1 = df1.loc[ linhas_vazias, : ].copy()
    
    # Excluir as linhas com a idade dos entregadores vazia
    linhas_vazias = df1[ 'Festival' ] != "NaN "
    df1 = df1.loc[ linhas_vazias, : ].copy()
    
    
    # Conversao coluna Delivery_person_Age de texto/categoria/string para numeros inteiros (int)
    df1[ 'Delivery_person_Age' ] = df1[ 'Delivery_person_Age' ].astype( int )
    
    # Converter coluna Delivery_person_Ratings de texto/categoria/strings para numeros decimais (float)
    df1[ 'Delivery_person_Ratings' ] = df1['Delivery_person_Ratings'].astype( float )
    
    # Converter coluna Order_Date de texto/string para Data
    # Nota: na condicional ( format='%d-%m-%Y' ) o Y (ano) sempre e maiusculo
    df1[ 'Order_Date' ] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    
    # Converter a coluna multiple_deliveries de texto/string para numeros inteiros (int) e removendo linhas vazias
    linhas_vazias = (df1['multiple_deliveries'] != "NaN ")
    df1 = df1.loc[ linhas_vazias, : ].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    # Remover spaco da string usando strip em vez de for (e necessario converter tipo series para str)
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    
    # 7. Limpando a coluna de time taken
    
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype( int )

    return df1

# Import

df = pd.read_csv('dataset/train.csv')

# clean dataset

df1 =  clean_code( df )

# ================================ Inicio da Estrutura logica do codigo =================================
# Importando os dados




# ============================================================================
# Side Bar with Filter (Barra Lateral)
# ============================================================================



st.header('Marketplace - Visão Empresa')

# image_path = 'projeto_logo.png'

image = Image.open( 'projeto_logo.png' )
st.sidebar.image( image, width=210 )

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown( '## Selecione uma data limite' )

date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.sidebar.markdown( """---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS' )

#Filter Date (Filtro de date)
linhas_selecionadas = df1[ 'Order_Date' ] < date_slider
df1 = df1.loc[ linhas_selecionadas, : ]

# filter traffic (filtro de transito)
linhas_selecionadas = df1[ 'Road_traffic_density' ].isin( traffic_options )
df1 = df1.loc[ linhas_selecionadas, : ]


# ============================================================================
# Layout streamlit 
# ============================================================================


# ======================= TAB1 ===============================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geografica'] )
    
with tab1:
    with st.container():
        fig = order_metric( df1 )
        st.markdown( '# Order by Day')
        st.plotly_chart( fig, use_container_width=True )

        
    
   
    with st.container():
        col1, col2 = st.columns( 2 )
        
        with col1:
            fig = traffic_order_share( df1 )
            st.header( 'Traffic Order Share' )
            st.plotly_chart( fig, use_container_width=True )
          
            
            
                    
        with col2:
            fig = traffic_order_city( df1 )
            st.plotly_chart( fig, use_container_width=True )
            st.header( 'Traffic Order Citry' )
            

# ======================= TAB2 ===============================================

with tab2:
    with st.container():
        fig = order_by_week( df1 )
        st.markdown( '# Order by Week' )
        st.plotly_chart( fig, use_container_widht=True )
        

        
        
    with st.container():
        st.markdown('# Order Share by Week')
        fig = order_share_by_week( df1 )
        st.plotly_chart( fig, use_container_widht=True)

        


# ======================= TAB3 ===============================================

with tab3:
    with st.container():
        st.markdown( '# Country Maps') 
        country_maps( df1 )
        
        
        

    
