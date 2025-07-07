import streamlit as st
from PIL import Image
import os
import pandas as pd

st.set_page_config(page_title="Roteirizador Alphaville", layout="centered")

# Centraliza e exibe a logo
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.jpg", use_container_width=False, width=150)

st.title("📍 Roteirizador Alphaville por Imagem")
st.markdown("Selecione o número do lote para visualizar a rota.")

# Lista de arquivos de rota disponíveis
arquivos = sorted([f for f in os.listdir(".") if f.endswith(".png") and f[:3].isdigit()])
ids_disponiveis = sorted(set(int(f[:3]) for f in arquivos))

# Carregar planilha de descrições
try:
    df_rotas = pd.read_excel("descritivo_rotas.xlsx")
except Exception as e:
    st.error(f"Erro ao carregar a planilha: {e}")
    df_rotas = pd.DataFrame(columns=["LOTE", "ROTA"])

# Lista suspensa
lote_id = st.selectbox("Selecione o número do lote:", ids_disponiveis, format_func=lambda x: f"Lote {x}")

# Imagem da rota
rota_img_path = f"{lote_id:03d}.png"
if os.path.exists(rota_img_path):
    st.image(rota_img_path, caption=f"Rota até o Lote {lote_id}", use_container_width=True)
else:
    st.warning(f"Imagem da rota ({rota_img_path}) não encontrada.")

# Imagem da casa
casa_img_path = f"casa_{lote_id:03d}.jpeg"
if os.path.exists(casa_img_path):
    st.image(casa_img_path, caption=f"Imagem da casa no Lote {lote_id}", use_container_width=True)
else:
    st.warning(f"Imagem da casa ({casa_img_path}) não encontrada.")

# Descrição do percurso
desc = df_rotas[df_rotas["LOTE"] == lote_id]["ROTA"]
if not desc.empty:
    st.info(f"📌 **Descrição da rota:** {desc.values[0]}")
else:
    st.warning("Descrição da rota não encontrada na planilha.")
