import streamlit as st
from PIL import Image
import os

st.set_page_config(page_title="Roteirizador Alphaville", layout="centered")
st.title("📍 Roteirizador Alphaville por Imagem")
st.markdown("Insira o número do lote para visualizar a rota pré-calculada.")

# Entrada do número do lote
lote_id = st.number_input("Digite o número do lote:", min_value=1, step=1)

# Constrói o nome da imagem
nome_arquivo = f"{lote_id:03d}.png"
caminho = os.path.join(".", nome_arquivo)

# Verifica e exibe a imagem correspondente
if os.path.exists(caminho):
    imagem = Image.open(caminho)
    st.image(imagem, caption=f"Rota até o Lote {lote_id}", use_column_width=True)
else:
    st.warning(f"Imagem para o Lote {lote_id} não encontrada ({nome_arquivo}).")
