from haversine import haversine
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import pandas as pd
from PIL import Image
import folium
import streamlit as st
from streamlit_folium import folium_static
import numpy as np

st.set_page_config( page_title='Visão Restaurante', page_icon='🍲️', layout='wide' )

# -------------------------- Funções --------------------------

def avg_std_time_on_traffic( df1 ):
    df_aux = ( df1.loc[ :, ['City', 'Time_taken(min)','Road_traffic_density'] ]
                  .groupby( ['City', 'Road_traffic_density'] )
                  .agg( {'Time_taken(min)': ['mean', 'std' ] } ) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time'] ) )

    return fig 



def avg_std_time_graph( df1 ):
    df_aux = (df1.loc[ :, ['City', 'Time_taken(min)'] ]
                 .groupby( ['City'] )
                 .agg( {'Time_taken(min)': ['mean', 'std' ] } ))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))

    return fig


def av_std_time_delivery( df1, festival, op):
    '''
        Esta função calcula o tempo médio e o desvio padão do tempo de entrega.
        Parâmetros:
        Input:
        - df: Dataframe com os dados necessarios para o calculo 
        - op: Tipo de operação que precisa ser calculado
            'avg-time': Calcula o tempo medio 
            'std_time' calcula o desvio padrao do tempo.
            Output:
            - df: Dataframe com 2 colunas e 1 linha.
    '''

    
    df_aux = ( df1.loc[ :, ['Festival', 'Time_taken(min)'] ]
                  .groupby( ['Festival'] )
                  .agg( {'Time_taken(min)': ['mean', 'std' ] } ) )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2 )
    

    return df_aux


def distance( df1, fig ):
        if fig == False:
            cols = ['Restaurant_latitude','Restaurant_longitude',
                    'Delivery_location_latitude','Delivery_location_longitude']
            df1['distance'] = df1.loc[:, cols].apply( lambda x: 
                                        haversine ( ( x['Restaurant_latitude'], x['Restaurant_longitude'] ), 
                                        (x ['Delivery_location_latitude'], x['Delivery_location_longitude'] ) ), axis=1 )
            
            avr_distance = np.round( df1['distance'].mean(), 2 )

            return avr_distance

        else:
            cols = ['Restaurant_latitude','Restaurant_longitude',
                    'Delivery_location_latitude','Delivery_location_longitude']
            df1['distance'] = df1.loc[:, cols].apply( lambda x: 
                                        haversine ( ( x['Restaurant_latitude'], x['Restaurant_longitude'] ), 
                                        (x ['Delivery_location_latitude'], x['Delivery_location_longitude'] ) ), axis=1 )
            
            avg_distance = df1.loc[ : ,[ 'City','distance'] ].groupby( ['City'] ).mean().reset_index()
            fig = go.Figure( data=[go.Pie( labels=avg_distance[ 'City' ], values=avg_distance[ 'distance' ], pull=[0, 0.1, 0])])

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
    df1 = df.copy()
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
df = pd.read_csv( 'dataset/train.csv' )

# Clean dataset
df1 = clean_code( df )

# ============================================================================
# Side Bar with Filter (Barra Lateral)
# ============================================================================



st.header('Marketplace - Restaurante')

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

condicao_climatica = st.sidebar.multiselect(
    'Quais as condições do climáticas',
    ['conditions Sunny','conditions Stormy',
    'conditions Sandstorms','conditions Windy',
    'conditions Fog','conditions Cloudy'],
    default=['conditions Sunny','conditions Stormy',
    'conditions Sandstorms','conditions Windy',
    'conditions Fog','conditions Cloudy'])
    
st.sidebar.markdown('### Powered by Comunidade DS' )

#Filter Date (Filtro de date)
linhas_selecionadas = df1[ 'Order_Date' ] < date_slider
df1 = df1.loc[ linhas_selecionadas, : ]

# filter traffic (filtro de transito)
linhas_selecionadas = df1[ 'Road_traffic_density' ].isin( traffic_options )
df1 = df1.loc[ linhas_selecionadas, : ]

linhas_selecionadas = df1['Weatherconditions'].isin( condicao_climatica )
df1 = df1.loc[ linhas_selecionadas, :]


# =============================================================
# Layout Streamlit
# =============================================================


tab1, tab2= st.tabs( ['Visão Gerencial', '-'] )

with tab1:
    with st.container():
        st.markdown("""---""")
        st.title( 'Over Matrics' )

        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        with col1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric( 'A quantidade de entregadores é:', delivery_unique)
            
        with col2:
            avr_distance = distance( df1, fig=False )
            col2.metric( 'A distância média das entregas', avr_distance )         

            
        with col3:
            df_aux = av_std_time_delivery( df1, 'Yes', 'avg_time')
            col3.metric( 'Tempo médio de entrega c/ Festival',df_aux )    

            
        with col4:
            df_aux = av_std_time_delivery( df1, 'Yes', 'std_time')
            col4.metric( 'STD entrega',df_aux )
            
            
        with col5:
            df_aux = av_std_time_delivery( df1, 'No', 'avg_time')
            col5.metric( 'Tempo padrão médio de entrega c/ Festival',df_aux )

        
        with col6:
            df_aux = av_std_time_delivery( df1, 'No', 'std_time')
            col6.metric( 'STD entrega',df_aux )
            
            

    with st.container():
        st.markdown('### Tempo médio de entrega por cidade' )
        col1, col2 = st.columns( 2 )
        with col1:
            fig = avg_std_time_graph( df1 )
            st.plotly_chart( fig )
            
                
    
        with col2:
            st.markdown('### Dsstribuição da Distância')
        
            df_aux = ( df1.loc[ :, ['City', 'Time_taken(min)','Type_of_order'] ]
                      .groupby( ['City', 'Type_of_order'] )
                      .agg( {'Time_taken(min)': ['mean', 'std' ] } ) )

            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            st.dataframe( df_aux )
   

    with st.container():
        st.markdown("""---""")
        st.title( 'Distribuição do Tempo' )
        col1, col2 = st.columns( 2 )
        with col1:
            fig = distance( df1, fig=True )
            st.plotly_chart( fig )
       
        
        with col2:
            fig = avg_std_time_on_traffic( df1 )
            st.plotly_chart( fig )
            
                
            
              
    


