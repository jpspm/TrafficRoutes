import folium
import pandas as pd
from geopy.distance import geodesic
import networkx as nx

# Função para ler nomes e coordenadas de locais de um arquivo de texto
def ler_locais(nome_arquivo):
    locais = {}
    with open(nome_arquivo, 'r', encoding='utf-8') as arquivo:
        for linha in arquivo:
            partes = linha.strip().split(',')
            if len(partes) == 3:
                titulo, latitude, longitude = [parte.strip() for parte in partes]
                locais[titulo] = (float(latitude), float(longitude))
            else:
                print(f"Formato inválido na linha: {linha}")
    return locais

# Nome do arquivo de texto que contém os locais no formato "título, latitude, longitude"
arquivo_locais = 'estacoes.txt'

# Lê os nomes e coordenadas dos locais do arquivo de texto
locais = ler_locais(arquivo_locais)

# Inicialize uma matriz vazia para armazenar as distâncias
matriz_distancias = {}

# Calcula as distâncias entre todos os pares de locais
for local1, coord1 in locais.items():
    for local2, coord2 in locais.items():
        # Não calcule a distância entre o mesmo local
        if local1 != local2:
            # Calcula a distância geodésica entre os locais
            distancia = geodesic(coord1, coord2).kilometers
            matriz_distancias[(local1, local2)] = distancia

            print(f'Distância entre {local1} e {local2} em km é {distancia}')

# Agora, 'matriz_distancias' contém as distâncias entre todos os pares de locais
# A chave da matriz é uma tupla com os títulos dos locais

# Cálculo do Minimum Spanning Tree (Árvore Geradora Mínima) usando o algoritmo PRIM
# Vamos criar um grafo com NetworkX usando as distâncias
grafo = nx.Graph()
for local1, local2 in matriz_distancias.keys():
    peso = matriz_distancias[(local1, local2)]
    grafo.add_edge(local1, local2, weight=peso)

# Calcula a Árvore Geradora Mínima usando o algoritmo PRIM
arvore_minima = nx.minimum_spanning_tree(grafo)

# Escreve a Árvore Geradora Mínima em um arquivo de saída
saida_arquivo = 'arvore_minima.txt'
with open(saida_arquivo, 'w') as arquivo_saida:
    for aresta in arvore_minima.edges(data=True):
        local1, local2, data = aresta
        peso = data['weight']
        arquivo_saida.write(f'{local1}, {local2}, {peso}\n')

print(f'A Árvore Geradora Mínima foi escrita no arquivo: {saida_arquivo}')

# Criar um mapa
m = folium.Map(location=[-8.052238, -34.913213], zoom_start=12)

# Adicionar marcadores para os locais (pontos)
for local in locais:
    latitude, longitude = locais[local]
    folium.Marker([latitude, longitude], tooltip=local).add_to(m)

# Ler o arquivo de saída com as arestas da Árvore Geradora Mínima
df = pd.read_csv(saida_arquivo, sep=',')

# Adicionar linhas para as rotas da Árvore Geradora Mínima
for _, row in df.iterrows():
    local1, local2, peso = row
    lat1, lon1 = locais[local1.strip()]  # Removendo espaços em branco extras
    lat2, lon2 = locais[local2.strip()]  # Removendo espaços em branco extras
    folium.PolyLine([(lat1, lon1), (lat2, lon2)], color='blue', weight=2.5).add_to(m)

# Salvar o mapa como um arquivo HTML
mapa_saida = 'mapa_rotas.html'
m.save(mapa_saida)

print(f'O mapa das rotas foi salvo em: {mapa_saida}')
