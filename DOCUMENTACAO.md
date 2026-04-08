# Documentação Técnica — Visualização de Trajetórias com Grafos

## Sumário

1. [Visão Geral](#visão-geral)
2. [Formato dos Dados de Entrada](#formato-dos-dados-de-entrada)
3. [Módulos e Pacotes Utilizados](#módulos-e-pacotes-utilizados)
4. [Funções do Projeto](#funções-do-projeto)
   - [processar_trajetorias](#processar_trajetorias)
   - [dfs_recursivo](#dfs_recursivo)
   - [estatisticas_trajetorias](#estatisticas_trajetorias)
   - [plotar_grafos](#plotar_grafos)
5. [Fluxo de Execução](#fluxo-de-execução)
6. [Conceitos Aplicados](#conceitos-aplicados)

---

## Visão Geral

O programa lê arquivos de texto contendo as posições de pessoas rastreadas por câmeras ao longo de vários frames de vídeo. Para cada pessoa, constrói um **grafo dirigido** onde cada nó é uma posição `(x, y)` e cada aresta representa o deslocamento entre dois frames consecutivos. Por fim, plota todas as trajetórias no mesmo gráfico com cores distintas.

---

## Formato dos Dados de Entrada

Os arquivos `Paths_D.txt` e `Paths_N.txt` seguem este padrão:

```
[95]
96 (1179,476,1)(1179,476,2)(1178,470,3)...
99 (1083,948,1)(1082,946,2)(1082,943,3)...
```

- `[95]` — cabeçalho indicando o número total de pessoas no arquivo
- `96` — identificador numérico da pessoa
- `(1179, 476, 1)` — coordenada no formato `(x, y, frame)`
  - `x`, `y`: posição em pixels no espaço da câmera
  - `frame`: número do quadro de vídeo em que a pessoa foi detectada

---

## Módulos e Pacotes Utilizados

```python
import networkx as nx        # criação e manipulação de grafos
import matplotlib.pyplot as plt  # plotagem do gráfico
import matplotlib.cm as cm       # mapas de cores
import numpy as np               # geração de valores numéricos (linspace)
import re                        # expressões regulares para parsing do arquivo
```

Todos são **módulos externos** (instalados via pip), exceto `re`, que é um **módulo da biblioteca padrão** do Python. O uso de `import ... as` é um recurso de módulos que cria um alias para facilitar o uso ao longo do código.

---

## Funções do Projeto

### `processar_trajetorias`

```python
def processar_trajetorias(caminho_ficheiro):
```

**Responsabilidade:** ler o arquivo, separar os dados de cada pessoa e construir um grafo dirigido para cada trajetória.

#### Passo 1 — Leitura do arquivo

```python
with open(caminho_ficheiro, 'r') as f:
    conteudo = f.read()
```

Abre o arquivo e lê todo o conteúdo de uma vez como uma string. O `with` garante que o arquivo seja fechado automaticamente ao final do bloco.

#### Passo 2 — Remoção do cabeçalho

```python
conteudo = re.sub(r'\[\d+\]', '', conteudo)
```

A função `re.sub` substitui qualquer ocorrência do padrão `[N]` (como `[95]`) por uma string vazia, removendo o cabeçalho. O padrão regex `\[\d+\]` significa:
- `\[` e `\]` — colchetes literais (escapados pois têm significado especial em regex)
- `\d+` — um ou mais dígitos

#### Passo 3 — Divisão por pessoa

```python
blocos = re.split(r'(?=\b\d+\s+\()', conteudo)
```

Este é o ponto central do parsing. O padrão usa um **lookahead** `(?=...)` — divide o texto nos pontos onde encontra um número seguido de espaço e `(`, sem consumir esses caracteres. Isso garante que cada bloco começa com o ID da pessoa. Exemplo:

```
"96 (1179,476,1)...  99 (1083,948,1)..."
 ↑                    ↑
 divide aqui          divide aqui
```

#### Passo 4 — Extração das coordenadas

```python
pontos_str = re.findall(r'\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)', bloco)
```

`re.findall` retorna uma lista de tuplas com os três grupos capturados de cada `(x, y, frame)`. O padrão:
- `\(` e `\)` — parênteses literais
- `([^,]+)` — captura tudo até a próxima vírgula (os valores de x, y e frame)
- `\s*` — ignora espaços em branco ao redor

#### Passo 5 — Construção do grafo

```python
G_pessoa = nx.DiGraph()
G_pessoa.add_edge(origem, destino)
```

Para cada par de posições consecutivas `(caminho[i], caminho[i+1])`, adiciona uma aresta dirigida ao grafo. O resultado é um `DiGraph` (grafo dirigido) onde:
- **Nós** são posições `(x, y)`
- **Arestas** representam o movimento de uma posição para a próxima

```
(1179,476) → (1179,476) → (1178,470) → (1178,464) → ...
```

---

### `dfs_recursivo`

```python
def dfs_recursivo(G, no, visitados=None):
```

**Responsabilidade:** percorrer o grafo em profundidade a partir de um nó inicial, retornando todos os nós alcançáveis. Utiliza **recursividade**.

#### Como funciona a recursão

A **recursividade** ocorre quando uma função chama a si mesma. Aqui, `dfs_recursivo` chama `dfs_recursivo` para explorar os vizinhos do nó atual:

```python
if visitados is None:
    visitados = set()       # caso base de inicialização

visitados.add(no)           # marca o nó atual como visitado

for vizinho in G.successors(no):
    if vizinho not in visitados:
        dfs_recursivo(G, vizinho, visitados)  # CHAMADA RECURSIVA

return visitados
```

#### Caso base

A recursão para quando o laço `for` não encontra nenhum vizinho novo para explorar — todos os vizinhos já estão em `visitados`. Nesse momento, a função retorna sem fazer nova chamada recursiva.

#### Exemplo visual da pilha de chamadas

Considere o trecho de grafo: `A → B → C → D`

```
dfs_recursivo(G, A)
  visita A
  chama dfs_recursivo(G, B)
    visita B
    chama dfs_recursivo(G, C)
      visita C
      chama dfs_recursivo(G, D)
        visita D
        sem vizinhos novos → retorna {A, B, C, D}
      retorna {A, B, C, D}
    retorna {A, B, C, D}
  retorna {A, B, C, D}
```

#### Por que `visitados` é um conjunto (`set`)?

O conjunto garante que cada nó seja visitado no máximo uma vez, evitando loops infinitos em grafos com ciclos (ex: pessoa que volta à mesma posição). A verificação `if vizinho not in visitados` tem custo O(1) em um `set`.

#### Por que `visitados=None` e não `visitados=set()`?

Em Python, usar um objeto mutável como valor padrão de parâmetro (`def f(x=[])`) é um erro clássico: o mesmo objeto é compartilhado entre todas as chamadas. Usar `None` e criar o `set` dentro da função garante que cada chamada inicial crie seu próprio conjunto independente.

---

### `estatisticas_trajetorias`

```python
def estatisticas_trajetorias(grafos_pessoas):
```

**Responsabilidade:** usar o DFS recursivo para calcular e exibir estatísticas sobre as trajetórias.

```python
for i, G in enumerate(grafos_pessoas):
    no_inicial = list(G.nodes)[0]
    nos_visitados = dfs_recursivo(G, no_inicial)
    tamanhos.append(len(nos_visitados))

print(f"  Posições únicas — mín: {min(tamanhos)}, máx: {max(tamanhos)}, média: {sum(tamanhos) / len(tamanhos):.1f}")
```

Para cada grafo de pessoa, inicia o DFS a partir do primeiro nó e conta quantas posições únicas foram visitadas. O `:.1f` na f-string formata o número com 1 casa decimal.

---

### `plotar_grafos`

```python
def plotar_grafos(grafos_pessoas, pos, titulo="Trajetórias"):
```

**Responsabilidade:** desenhar todas as trajetórias no mesmo gráfico, cada uma com uma cor diferente.

#### Geração de cores

```python
cores = cm.turbo(np.linspace(0, 1, num_pessoas))
```

- `np.linspace(0, 1, N)` — gera N valores igualmente espaçados entre 0 e 1
- `cm.turbo(...)` — mapeia cada valor para uma cor do gradiente `turbo` (azul → verde → amarelo → vermelho)

O resultado é que cada pessoa recebe uma cor visualmente distinta.

#### Plotagem do grafo

```python
nx.draw(G, pos, node_size=0, edge_color=[cores[i]], arrows=True, arrowsize=7, alpha=0.6, width=1.5)
```

- `pos` — dicionário `{(x,y): (x, -y)}` que define onde desenhar cada nó na tela. O `-y` inverte o eixo vertical para que o gráfico corresponda à orientação real da câmera (em pixels, y cresce para baixo)
- `node_size=0` — oculta os nós; apenas as arestas (o caminho) são visíveis
- `arrows=True` — desenha setas indicando a direção do movimento
- `alpha=0.6` — transparência de 60%, permitindo ver sobreposições entre trajetórias

---

## Fluxo de Execução

```
main.py é executado
│
├── Para cada arquivo (Paths_D.txt, Paths_N.txt):
│   │
│   ├── processar_trajetorias(arquivo)
│   │   ├── Lê o arquivo inteiro
│   │   ├── Remove cabeçalho [N]
│   │   ├── Divide em blocos por pessoa (regex)
│   │   └── Para cada bloco:
│   │       ├── Extrai coordenadas (x, y, frame)
│   │       ├── Cria DiGraph
│   │       └── Adiciona arestas entre posições consecutivas
│   │
│   ├── estatisticas_trajetorias(grafos)
│   │   └── Para cada grafo:
│   │       └── dfs_recursivo(G, nó_inicial)  ← recursão
│   │           └── Retorna conjunto de nós visitados
│   │
│   └── plotar_grafos(grafos, pos, titulo)
│       ├── Gera paleta de cores
│       ├── Desenha cada grafo com nx.draw
│       └── Exibe o gráfico
```

---

## Conceitos Aplicados

| Conceito | Onde aparece no código |
|---|---|
| **Funções** | `processar_trajetorias`, `dfs_recursivo`, `estatisticas_trajetorias`, `plotar_grafos` |
| **Recursividade** | `dfs_recursivo` chama a si mesma para explorar vizinhos |
| **Módulos** | `import re` (biblioteca padrão) |
| **Pacotes** | `import networkx`, `matplotlib`, `numpy` (pacotes externos) |
| **Estruturas de dados** | listas, dicionários, conjuntos (`set`) |
| **Manipulação de arquivos** | `open`, `f.read()` |
| **Expressões regulares** | `re.sub`, `re.split`, `re.findall` |
| **f-strings** | formatação de saída no terminal |
| **Tratamento de exceções** | `try/except FileNotFoundError` |
