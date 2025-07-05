import streamlit as st
import geopandas as gpd
import folium
import osmnx as ox
import networkx as nx
from shapely.geometry import Point
from streamlit_folium import st_folium

# Carregar GeoJSON com tratamento de erro
try:
    gdf = gpd.read_file("pontos.geojson")
except Exception as e:
    st.error("Erro ao carregar o arquivo pontos.geojson. Verifique se ele está presente no diretório raiz do projeto.")
    st.stop()

# Definir CRS e converter
gdf = gdf.set_crs("EPSG:4326")

# Identificar portaria
portaria = gdf[gdf['local'] == 'portaria'].iloc[0]

# Baixar grafo de ruas com OSMnx em EPSG:4326 (não projetado)
center_point = (portaria.geometry.y, portaria.geometry.x)
G = ox.graph_from_point(center_point, dist=1500, network_type='drive')

# Streamlit UI
st.title("Roteirizador Alphaville com Ruas Reais")
lote_id = st.number_input("Digite o número do lote:", min_value=1, step=1)

if lote_id:
    destino = gdf[gdf['id'] == lote_id]
    if destino.empty:
        st.error("Lote não encontrado.")
    else:
        destino = destino.iloc[0]

        # Encontrar nós mais próximos na rede (usando lon/lat)
        orig_node = ox.distance.nearest_nodes(G, portaria.geometry.x, portaria.geometry.y)
        dest_node = ox.distance.nearest_nodes(G, destino.geometry.x, destino.geometry.y)

        # Calcular rota
        route = nx.shortest_path(G, orig_node, dest_node, weight='length')
        route_coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]

        # Criar mapa
        m = folium.Map(location=[portaria.geometry.y, portaria.geometry.x], zoom_start=16)
        folium.Marker([portaria.geometry.y, portaria.geometry.x], tooltip="Portaria", icon=folium.Icon(color='green')).add_to(m)
        folium.Marker([destino.geometry.y, destino.geometry.x], tooltip=f"Lote {lote_id}", icon=folium.Icon(color='blue')).add_to(m)
        folium.PolyLine(route_coords, color='blue').add_to(m)

        st_folium(m, width=700, height=500)
