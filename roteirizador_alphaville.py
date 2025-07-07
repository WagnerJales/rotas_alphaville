import streamlit as st
from PIL import Image
import os

st.set_page_config(page_title="Roteirizador Alphaville", layout="centered")
st.title("📍 Roteirizador Alphaville")
st.markdown("Selecione o número do lote para visualizar a rota.")

# Gera lista de imagens disponíveis (formato 001.png, 002.png, ...)
arquivos = sorted([f for f in os.listdir(".") if f.endswith(".png") and f[:3].isdigit()])
ids_disponiveis = sorted(set(int(f[:3]) for f in arquivos))

# Lista suspensa para seleção do lote
lote_id = st.selectbox("Selecione o número do lote:", ids_disponiveis, format_func=lambda x: f"Lote {x}")

# Constrói o nome da imagem
nome_arquivo = f"{lote_id:03d}.png"
caminho = os.path.join(".", nome_arquivo)

# Verifica e exibe a imagem correspondente
if os.path.exists(caminho):
    imagem = Image.open(caminho)
    st.image(imagem, caption=f"Rota até o Lote {lote_id}", use_container_width=True)
else:
    st.warning(f"Imagem para o Lote {lote_id} não encontrada ({nome_arquivo}).")

st.image("logo.png", use_container_width=False, width=150)
