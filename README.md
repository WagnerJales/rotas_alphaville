
# Roteirizador Alphaville

Aplicação Streamlit para roteirização de acesso a residências em condomínio de alto padrão, usando dados reais de ruas do OpenStreetMap.

## Funcionalidade

- Entrada do número do lote na portaria
- Cálculo de rota mais curta via ruas reais até o lote
- Exibição interativa em mapa com markers e linha de rota

## Requisitos

Instale as dependências:

```bash
pip install streamlit geopandas osmnx networkx streamlit-folium
```

## Execução

Certifique-se de que todos os arquivos `.shp`, `.dbf`, `.shx`, `.prj`, `.cpg` estão no mesmo diretório do script.

Execute o app com:

```bash
streamlit run roteirizador_alphaville.py
```

## Estrutura dos arquivos

- `roteirizador_alphaville.py`: script principal do app
- `pontos.shp` e arquivos auxiliares: pontos da portaria e lotes

## Observações

- Usa OSMnx para obter a malha viária local
- Distância padrão de busca por ruas: 1000 metros a partir da portaria
- Rota baseada em menor distância (peso 'length')

## Melhorias futuras

- Cache local do grafo de ruas
- Integração com autenticação de visitantes
- Geração de QR code para envio da rota
