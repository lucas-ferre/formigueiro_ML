# Formigueiro ML - Algoritmo de Colônia de Formigas (ACO)

Um ambiente interativo e educacional em Python para exploração e visualização em tempo real de **Otimização por Colônia de Formigas (*Ant Colony Optimization - ACO*)** e Inteligência de Enxame (*Swarm Intelligence*).

<p align="center">
  <img src="formigas.gif" alt="Demonstração do Formigueiro ML" width="750" />
</p>
---

## Recursos Principais

### 1. Modo Otimização de Rotas (TSP - Caixeiro Viajante)
- **Visualização de Trilhas de Feromônio**: Renderização da matriz $\tau_{ij}$ com intensidade luminosa e espessura proporcional ao feromônio acumulado.
- **Animação das Formigas**: Acompanhe o deslocamento das formigas explorando os nós e convergindo para a rota ótima global.
- **Gráfico de Convergência em Tempo Real**: Curvas ao vivo da melhor distância e da distância média da colônia por iteração.
- **Interação Direta**:
  - *Clique com Botão Esquerdo*: Adiciona nova cidade/nó no mapa.
  - *Clique com Botão Direito*: Remove a cidade clicada.
  - *Arrastar*: Move cidades existentes recalculando as matrizes de distância dinamicamente.
- **Ajuste de Hiperparâmetros em Tempo Real**:
  - $\alpha$ (*Alpha*): Peso da memória coletiva (influência do feromônio).
  - $\beta$ (*Beta*): Peso da heurística de proximidade (visibilidade $1/d$).
  - $\rho$ (*Rho*): Taxa de evaporação do feromônio.
  - *Número de Formigas* e *Velocidade da Simulação*.

### 2. Modo Forrageamento & Labirinto (Grid Foraging 2D)
- **Estigmergia e Comunicação Indireta**: Formigas operam com dois tipos de feromônio:
  - 🟢 **Feromônio de Alimento (*Food Pheromone*)**: Deixado por formigas que encontraram comida e voltam ao ninho.
  - 🔵 **Feromônio de Ninho (*Home Pheromone*)**: Deixado por formigas ao sair em busca de alimento.
- **Paredes e Obstáculos Desenháveis**: Desenhe muros e labirintos com o mouse para observar como a colônia encontra o caminho mais curto ao redor de barreiras.
- **Presets de Mapas**: Teste instantaneamente com configurações de Barreira Central, Labirinto ou Área Livre.

---

## Fundamentação Matemática

### 1. Regra de Transição Probabilística
A probabilidade da formiga $k$ sair do nó $i$ para o nó $j$ é dada por:

$$P_{ij}^k = \frac{[\tau_{ij}]^\alpha \cdot [\eta_{ij}]^\beta}{\sum_{l \in \text{permitidos}} [\tau_{il}]^\alpha \cdot [\eta_{il}]^\beta}$$

Onde:
- $\tau_{ij}$ é o nível de feromônio na aresta $(i, j)$.
- $\eta_{ij} = \frac{1}{d_{ij}}$ é a informação heurística de visibilidade (inverso da distância euclidiana).

### 2. Evaporação e Atualização de Feromônio

$$\tau_{ij} \leftarrow (1 - \rho) \cdot \tau_{ij} + \sum_{k=1}^{m} \Delta \tau_{ij}^k + e \cdot \Delta \tau_{ij}^{\text{best}}$$

Onde $\Delta \tau_{ij}^k = \frac{Q}{L_k}$ é a contribuição inversamente proporcional ao tamanho da rota $L_k$ percorrida pela formiga $k$.

---

## Como Executar

### 1. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 2. Iniciar a Aplicação
```bash
python main.py
```

### 3. Executar os Testes Automatizados
```bash
python -m pytest tests
```

---

## ⌨ Atalhos do Teclado

| Tecla | Ação |
| :--- | :--- |
| `Espaço` | Iniciar / Pausar a simulação |
| `1` | Alternar para o modo **Caixeiro Viajante (TSP)** |
| `2` | Alternar para o modo **Forrageamento (Labirinto)** |
| `H` | Abrir / Fechar o painel de ajuda e equações |
| `Esc` | Fechar modal de ajuda ou sair |

---

## Estrutura do Projeto

```
formigueiro_ML/
├── core/
│   ├── aco_tsp.py          # Lógica do algoritmo ACO para TSP
│   ├── grid_foraging.py    # Simulação física e estigmérgica de forrageamento 2D
│   └── metrics.py          # Rastreamento de métricas e histórico de convergência
├── ui/
│   ├── colors.py           # Paleta de cores moderna (tema dark)
│   ├── widgets.py          # Botões, Sliders e Controles em Pygame
│   ├── chart_panel.py      # Renderizador do gráfico de fitness em tempo real
│   ├── visualizer_tsp.py   # Interface e animação do modo TSP
│   └── visualizer_grid.py  # Interface e mapas de calor do modo Forrageamento
├── tests/
│   ├── test_aco.py         # Testes matemáticos e algorítmicos
│   └── test_ui.py          # Testes de ciclo de vida e interface headless
├── main.py                 # Ponto de entrada do programa
└── requirements.txt        # Dependências do projeto
```
