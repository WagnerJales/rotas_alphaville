import streamlit as st
import json
import osmnx as ox
import networkx as nx
import folium
from folium import plugins
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
from streamlit_folium import st_folium

# Configuração da página
st.set_page_config(
    page_title="Roteirizador Alphaville",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Roteirizador Alphaville")
st.markdown("**Encontre a rota mais curta entre a portaria e qualquer lote do condomínio**")

@st.cache_data
def carregar_pontos(arquivo_geojson):
    """Carrega os pontos do arquivo GeoJSON"""
    try:
        with open(arquivo_geojson, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        pontos = {}
        portaria = None
        
        for feature in data['features']:
            props = feature['properties']
            coords = feature['geometry']['coordinates']
            
            if props['id'] == 'portaria':
                portaria = {
                    'lat': coords[1],
                    'lon': coords[0],
                    'name': props['name']
                }
            else:
                pontos[props['id']] = {
                    'lat': coords[1],
                    'lon': coords[0],
                    'name': props['name']
                }
        
        return pontos, portaria
    except Exception as e:
        st.error(f"Erro ao carregar arquivo GeoJSON: {e}")
        return {}, None

@st.cache_data
def baixar_grafo_ruas(lat, lon, dist=2000):
    """Baixa o grafo de ruas usando OSMnx"""
    try:
        # Baixa o grafo de ruas em um raio de 2km
        G = ox.graph_from_point((lat, lon), dist=dist, network_type='drive')
        return G
    except Exception as e:
        st.error(f"Erro ao baixar grafo de ruas: {e}")
        return None

def encontrar_no_mais_proximo(G, lat, lon):
    """Encontra o nó mais próximo no grafo"""
    try:
        # Usa método mais simples sem projeção
        return ox.distance.nearest_nodes(G, lon, lat)
    except Exception as e:
        st.error(f"Erro ao encontrar nó mais próximo: {e}")
        return None

def calcular_rota(G, no_origem, no_destino):
    """Calcula a rota mais curta usando networkx"""
    try:
        # Usa grafo original para cálculo
        rota = nx.shortest_path(G, no_origem, no_destino, weight='length')
        return rota
    except Exception as e:
        st.error(f"Erro ao calcular rota: {e}")
        return None

def criar_mapa(portaria, lote_selecionado, G, rota):
    """Cria o mapa interativo com folium"""
    # Centro do mapa na portaria
    m = folium.Map(
        location=[portaria['lat'], portaria['lon']],
        zoom_start=16,
        tiles='OpenStreetMap'
    )
    
    # Marcador da portaria
    folium.Marker(
        [portaria['lat'], portaria['lon']],
        popup=f"<b>{portaria['name']}</b>",
        tooltip="Portaria",
        icon=folium.Icon(color='green', icon='home')
    ).add_to(m)
    
    # Marcador do lote
    folium.Marker(
        [lote_selecionado['lat'], lote_selecionado['lon']],
        popup=f"<b>{lote_selecionado['name']}</b>",
        tooltip=f"Lote {lote_selecionado['name']}",
        icon=folium.Icon(color='red', icon='flag')
    ).add_to(m)
    
    # Adiciona a rota ao mapa
    if rota and G:
        try:
            # Converte os nós da rota em coordenadas
            rota_coords = []
            for no in rota:
                lat = G.nodes[no]['y']
                lon = G.nodes[no]['x']
                rota_coords.append([lat, lon])
            
            # Adiciona a linha da rota
            folium.PolyLine(
                rota_coords,
                weight=5,
                color='blue',
                opacity=0.8,
                popup="Rota mais curta"
            ).add_to(m)
            
            # Calcula distância total
            distancia_total = sum(ox.utils_graph.get_route_edge_attributes(G, rota, 'length'))
            
            # Adiciona informação da distância
            folium.Marker(
                [portaria['lat'], portaria['lon']],
                popup=f"<b>Distância total: {distancia_total:.0f} metros</b>",
                icon=folium.DivIcon(html=f"""
                    <div style="background-color: white; border: 2px solid blue; border-radius: 5px; padding: 5px;">
                        <b>Distância: {distancia_total:.0f}m</b>
                    </div>
                """)
            ).add_to(m)
            
        except Exception as e:
            st.error(f"Erro ao adicionar rota ao mapa: {e}")
    
    return m

def main():
    # Carrega os pontos do arquivo GeoJSON
    pontos, portaria = carregar_pontos('pontos.geojson')
    
    if not portaria:
        st.error("Não foi possível carregar a portaria do arquivo GeoJSON")
        return
    
    if not pontos:
        st.error("Não foi possível carregar os lotes do arquivo GeoJSON")
        return
    
    # Interface do usuário
    st.sidebar.header("Configurações")
    
    # Lista dos lotes disponíveis
    lotes_disponiveis = list(pontos.keys())
    
    # Campo para selecionar o lote
    lote_id = st.sidebar.selectbox(
        "Selecione o número do lote:",
        options=lotes_disponiveis,
        format_func=lambda x: f"Lote {x}"
    )
    
    # Botão para calcular rota
    if st.sidebar.button("Calcular Rota", type="primary"):
        if lote_id in pontos:
            lote_selecionado = pontos[lote_id]
            
            with st.spinner("Baixando mapa de ruas..."):
                # Baixa o grafo de ruas
                G = baixar_grafo_ruas(portaria['lat'], portaria['lon'])
            
            if G:
                with st.spinner("Calculando rota mais curta..."):
                    # Encontra os nós mais próximos
                    no_portaria = encontrar_no_mais_proximo(G, portaria['lat'], portaria['lon'])
                    no_lote = encontrar_no_mais_proximo(G, lote_selecionado['lat'], lote_selecionado['lon'])
                    
                    if no_portaria and no_lote:
                        # Calcula a rota
                        rota = calcular_rota(G, no_portaria, no_lote)
                        
                        if rota:
                            # Cria o mapa (usando grafo original para coordenadas)
                            mapa = criar_mapa(portaria, lote_selecionado, G, rota)
                            
                            # Exibe o mapa
                            st.subheader(f"Rota da Portaria para o Lote {lote_id}")
                            st_folium(mapa, width=700, height=500)
                            
                            # Informações adicionais
                            distancia_total = sum(ox.utils_graph.get_route_edge_attributes(G, rota, 'length'))
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Distância Total", f"{distancia_total:.0f} m")
                            with col2:
                                st.metric("Número de Segmentos", len(rota) - 1)
                            with col3:
                                tempo_estimado = distancia_total / 1000 * 3  # 3 min por km (velocidade baixa)
                                st.metric("Tempo Estimado", f"{tempo_estimado:.1f} min")
                        else:
                            st.error("Não foi possível calcular a rota")
                    else:
                        st.error("Não foi possível encontrar os pontos no mapa de ruas")
            else:
                st.error("Não foi possível baixar o mapa de ruas")
        else:
            st.error("Lote não encontrado")
    
    # Informações sobre a aplicação
    with st.expander("ℹ️ Sobre esta aplicação"):
        st.markdown("""
        **Roteirizador Alphaville** é uma aplicação que calcula a rota mais curta entre a portaria 
        e qualquer lote do condomínio usando ruas reais.
        
        **Como funciona:**
        1. Selecione o número do lote desejado
        2. Clique em "Calcular Rota"
        3. A aplicação baixa o mapa de ruas da região
        4. Calcula a rota mais curta usando algoritmos de grafos
        5. Exibe o resultado no mapa interativo
        
        **Tecnologias utilizadas:**
        - **Streamlit**: Interface web
        - **OSMnx**: Download de mapas do OpenStreetMap
        - **NetworkX**: Cálculo de rotas
        - **Folium**: Mapas interativos
        """)

if __name__ == "__main__":
    main()


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
