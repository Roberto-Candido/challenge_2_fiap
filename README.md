# Otimizador de Cobertura com Algoritmo Genético

**Resumo:**  
Este projeto resolve o problema da cobertura ótima de pontos geográficos com o menor número de repetidores e custo, utilizando **Algoritmos Genéticos** (DEAP). A visualização dos resultados ocorre em um mapa interativo (Folium) integrado à interface web do Streamlit.

## Como funciona?

- Carregue um arquivo CSV com os pontos (nome, latitude, longitude)
- Defina os parâmetros do algoritmo (potências, custos, gerações, população)
- O algoritmo genético busca a configuração ideal: cobre todos os pontos com o menor número de repetidores e menor custo
- Visualize a configuração final e a evolução no mapa interativo

## Principais diferenciais

- **Otimização multiobjetivo:** minimiza custo e repetidores, maximizando a cobertura
- **AG customizado:** com operadores de cruzamento, mutação e seleção NSGA2
- **Visualização em tempo real:** mapa com cobertura, repetidores e evolução das soluções
- **Fácil de usar:** interface Streamlit intuitiva e pronta para receber novos conjuntos de pontos

## Estrutura do Projeto

- `main.py` — Interface principal Streamlit, integração dos módulos e visualização
- `ag_repetidores.py` — Definição e implementação do Algoritmo Genético para repetidores
- `utils.py` — Funções auxiliares (leitura de CSV, tratamento de dados)
- `visualizacao.py` — Funções de visualização geográfica (Folium) dos pontos e repetidores
- `data/pontos_exemplo.csv` — Dados de teste (exemplo de pontos geográficos)

## Como rodar

1. Instale as dependências:
   ```sh
   pip install -r requirements.txt
2. Execute a aplicação:
    ```sh
    streamlit run main.py