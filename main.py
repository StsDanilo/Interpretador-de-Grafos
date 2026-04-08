import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import re


def processar_trajetorias(caminho_ficheiro):
    """
    Lê um arquivo de trajetórias e retorna um grafo dirigido por pessoa.

    Formato esperado do arquivo:
        [N]          -> cabeçalho com número de pessoas
        ID (x,y,f)... -> ID da pessoa seguido de coordenadas (x, y, frame)

    Retorna:
        grafos_pessoas: lista de DiGraph, um por pessoa
        pos_global: dicionário {(x,y): (x, -y)} para plotagem
    """
    grafos_pessoas = []
    pos_global = {}

    with open(caminho_ficheiro, 'r') as f:
        conteudo = f.read()

    # Remove o cabeçalho [N] para não interferir na divisão dos blocos
    conteudo = re.sub(r'\[\d+\]', '', conteudo)

    # Divide o texto sempre que encontra um número solto seguido de '('
    # Cada bloco corresponde à trajetória de uma pessoa
    blocos = re.split(r'(?=\b\d+\s+\()', conteudo)

    for bloco in blocos:
        if not bloco.strip():
            continue

        # Extrai todas as coordenadas (x, y, frame) do bloco da pessoa
        pontos_str = re.findall(r'\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)', bloco)

        if not pontos_str:
            continue

        caminho = []
        for x_str, y_str, f_str in pontos_str:
            try:
                x = int(float(x_str))
                y = int(float(y_str))
                caminho.append((x, y))
            except ValueError:
                continue

        if len(caminho) > 0:
            G_pessoa = nx.DiGraph()

            # Adiciona o nó inicial (caso a pessoa não se mova entre frames)
            primeiro_ponto = caminho[0]
            G_pessoa.add_node(primeiro_ponto)
            pos_global[primeiro_ponto] = (primeiro_ponto[0], -primeiro_ponto[1])

            # Cria arestas entre posições consecutivas da pessoa
            for i in range(len(caminho) - 1):
                origem = caminho[i]
                destino = caminho[i + 1]

                # Se origem == destino (pessoa parada), o NetworkX cria um self-loop
                G_pessoa.add_edge(origem, destino)

                pos_global[origem] = (origem[0], -origem[1])
                pos_global[destino] = (destino[0], -destino[1])

            grafos_pessoas.append(G_pessoa)

    print(f"Arquivo '{caminho_ficheiro}': {len(grafos_pessoas)} trajetórias extraídas.")
    return grafos_pessoas, pos_global


def dfs_recursivo(G, no, visitados=None):
    """
    Percorre o grafo em profundidade (DFS) de forma recursiva a partir de um nó.

    A cada chamada, marca o nó atual como visitado e chama a si mesma
    para cada vizinho ainda não visitado — isso é a recursividade.

    Parâmetros:
        G: grafo dirigido (DiGraph)
        no: nó de partida
        visitados: conjunto de nós já visitados (None na primeira chamada)

    Retorna:
        visitados: conjunto com todos os nós alcançáveis a partir de 'no'
    """
    if visitados is None:
        visitados = set()

    visitados.add(no)

    for vizinho in G.successors(no):
        if vizinho not in visitados:
            dfs_recursivo(G, vizinho, visitados)  # chamada recursiva

    return visitados


def estatisticas_trajetorias(grafos_pessoas):
    """
    Usa o DFS recursivo para calcular quantas posições únicas
    cada pessoa visitou e exibe um resumo estatístico.
    """
    tamanhos = []

    for i, G in enumerate(grafos_pessoas):
        no_inicial = list(G.nodes)[0]
        nos_visitados = dfs_recursivo(G, no_inicial)
        tamanhos.append(len(nos_visitados))

    if tamanhos:
        print(f"  Posições únicas por trajetória — "
              f"mín: {min(tamanhos)}, máx: {max(tamanhos)}, "
              f"média: {sum(tamanhos) / len(tamanhos):.1f}")


def plotar_grafos(grafos_pessoas, pos, titulo="Trajetórias"):
    """
    Plota todas as trajetórias no mesmo gráfico, cada pessoa com uma cor diferente.
    """
    if not grafos_pessoas:
        print(f"Nenhuma trajetória para desenhar em '{titulo}'.")
        return

    plt.figure(figsize=(12, 8))
    num_pessoas = len(grafos_pessoas)

    # Gera uma cor distinta por pessoa usando o mapa de cores 'turbo'
    cores = cm.turbo(np.linspace(0, 1, num_pessoas))

    for i, G in enumerate(grafos_pessoas):
        nx.draw(
            G,
            pos,
            node_size=0,
            edge_color=[cores[i]],
            arrows=True,
            arrowsize=7,
            alpha=0.6,
            width=1.5
        )

    plt.title(f"{titulo} ({num_pessoas} pessoas encontradas)", fontsize=16)
    plt.axis('equal')
    plt.show()


# --- Execução Principal ---
if __name__ == "__main__":
    for arq, nome in [('Paths_D.txt', 'Câmara D'), ('Paths_N.txt', 'Câmara N')]:
        try:
            grafos, pos = processar_trajetorias(arq)
            estatisticas_trajetorias(grafos)
            plotar_grafos(grafos, pos, titulo=f"Trajetórias - {nome}")
        except FileNotFoundError:
            print(f"Erro: O arquivo '{arq}' não foi encontrado.")
