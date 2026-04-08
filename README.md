# Visualização de Trajetórias com Grafos

## Descrição

Sistema em Python que lê arquivos de trajetórias de pessoas captadas por câmeras e representa cada trajetória como um grafo dirigido. O resultado é exibido visualmente, com cada pessoa representada por uma cor diferente. O projeto aplica os conceitos de funções, recursividade, módulos e pacotes estudados em aula.

## Estrutura do Projeto

```
PythonProject1/
├── main.py          # Código principal
├── Paths_D.txt      # Dados de trajetórias — Câmara D
├── Paths_N.txt      # Dados de trajetórias — Câmara N
├── README.md        # Este arquivo
└── DOCUMENTACAO.md  # Explicação detalhada do código
```

## Dependências

- Python 3.x
- networkx
- matplotlib
- numpy

Instale as dependências:

```bash
pip install networkx matplotlib numpy
```

## Como Executar

```bash
python main.py
```

Os arquivos `Paths_D.txt` e `Paths_N.txt` devem estar na mesma pasta que `main.py`.

O programa irá processar os dois arquivos sequencialmente, imprimir estatísticas no terminal e abrir uma janela gráfica para cada câmera.

## Funcionalidades

| Funcionalidade | Conceito aplicado |
|---|---|
| Leitura e parsing dos arquivos | Manipulação de arquivos, expressões regulares |
| Separação das trajetórias por pessoa | Regex, estruturas de dados (listas, dicionários) |
| Construção do grafo de trajetória | Grafos dirigidos com NetworkX |
| Busca em profundidade (DFS) | **Recursividade** |
| Estatísticas de posições únicas | Funções, listas |
| Visualização colorida | Módulos matplotlib e numpy |

## Saída esperada

No terminal:
```
Arquivo 'Paths_D.txt': 95 trajetórias extraídas.
  Posições únicas por trajetória — mín: 1, máx: 99, média: 87.3
```

Em seguida, uma janela gráfica com as trajetórias de todas as pessoas plotadas sobre o espaço da câmera.
