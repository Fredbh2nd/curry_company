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

st.set_page_config( page_title='Visão Entregadores', page_icon='🛵️', layout='wide' )

# --------------------------- FUnções ---------------------------

def top_delivers( df1, top_asc ):
    df2 = ( df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
               .groupby( ['City', 'Delivery_person_ID' ] )
               .max().sort_values( ['City', 'Time_taken(min)'], ascending=top_asc ).reset_index() )

    df_aux1 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux3 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat( [df_aux1, df_aux2, df_aux3] ).reset_index( drop=True )

    return df3

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
# ============================================================================
# Side Bar with Filter (Barra Lateral)
# ============================================================================



st.header('Marketplace - Entregadores')

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


tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '-', '-'] )

with tab1:
    with st.container():
        st.title( 'Overal Metrics' )
        
        col1, col2, col3, col4 = st.columns( 4, gap='large')
        with col1:
            # A maior idade do Entregador
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric( 'Maior de idade', maior_idade )

        with col2:
            # A menor idade do Entregador
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric( 'Menor idade', menor_idade )

        with col3:
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric( 'Melhor condicao', melhor_condicao )


        with col4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric( 'Pior condicao', pior_condicao )

    with st.container():
        st.markdown ( """---""" )
        st.title( 'Avaliacoes' )

        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '###### Avaliacao media por Entregador' )
            avareg_for_ratings = ( df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings' ]]
                                  .groupby(['Delivery_person_ID']).mean()
                                  .reset_index() )
            st.dataframe( avareg_for_ratings )


        with col2:
            st.markdown( '###### Avaliacao media por transito' )


            df_avg_std_rating_by_trafic = ( df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                               .groupby(['Road_traffic_density'])
                                               .agg({'Delivery_person_Ratings' : ['mean' , 'std'] } ) )
            # mudar o nome da coluna
            df_avg_std_rating_by_trafic.columns = ['Delivery_men' , 'Delivery_std']
            # resetar o index
            df_avg_std_rating_by_trafic = df_avg_std_rating_by_trafic.reset_index()
            # exibir o dataframe
            st.dataframe( df_avg_std_rating_by_trafic )
            
            st.markdown( '###### Avaliacao media por clima' )
            df_avg_std_rating_by_weathers = ( df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                                 .groupby(['Weatherconditions'])
                                                 .agg({'Delivery_person_Ratings' : ['mean' , 'std'] } ) )
            # mudar o nome da coluna
            df_avg_std_rating_by_weathers.columns = ['Delivery_men' , 'Delivery_std']
            # resetar o index
            df_avg_std_rating_by_weathers = df_avg_std_rating_by_weathers.reset_index()
            # exibir o dataframe
            st.dataframe( df_avg_std_rating_by_weathers )

    with st.container():
        st.markdown ( """---""" )
        st.title( 'Velocidade de Entrega' )

        col1, col2 = st.columns( 2 )
        with col1:            
            st.markdown( '###### Top Entregadores mais rapidos' )
            df3 = top_delivers( df1, top_asc=False )
            st.dataframe( df3 )
                     
            
        with col2:
            df3 = top_delivers
            st.markdown( '###### Top Entregadores mais lentos' )
            df3 = top_delivers( df1, top_asc=True )
            st.dataframe( df3 )
            
    
                
            









    

