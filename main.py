import streamlit as st
import os
import random
import pandas as pd
import altair as alt
from utils import carregar_pontos_csv
from ag_repetidores import criar_toolbox_repetidores
from visualizacao import plotar_repetidores, plotar_pontos_simples
from streamlit_folium import st_folium
from deap import tools

st.set_page_config(page_title="Otimização de Repetidores", layout="wide")

st.title("Cobertura ótima com mínimo de repetidores")
st.write("O algoritmo busca cobrir todos os pontos com o menor número de repetidores possível.")

data_dir = "data"
default_file = os.path.join(data_dir, "pontos_exemplo.csv")

uploaded = st.file_uploader("Carregue seu arquivo CSV (nome,lat,lon)", type="csv")
if uploaded:
    pontos = carregar_pontos_csv(uploaded)
    st.success("Arquivo carregado!")
else:
    pontos = carregar_pontos_csv(default_file)
    st.info("Usando arquivo de exemplo.")

if pontos:
    st.subheader("Pontos candidatos:")
    st.dataframe(pontos)

    potencias = st.multiselect(
        "Potências possíveis (em km)", [10, 20, 50, 60, ],
        default=[ 10, 20, 50, 60],
    )

    custos_potencias = [600, 1200, 4000, 5000]
    n_gen = st.slider("Gerações", 10, 200, 60, 1)
    pop_size = st.slider("Tamanho da população", 10, 100, 30, 1)

    col1, col2, col3 = st.columns([1, 1, 2])
    with col3:
        buscar = st.button("Encontrar configuração ótima", use_container_width=False)

    if "resultados_calculados" not in st.session_state:
        st.markdown("#### Visualização dos pontos (antes da otimização)")
        mapa_pontos = plotar_pontos_simples(pontos)
        st_folium(mapa_pontos, width="100%", height=500, key="mapa_inicial")

    if buscar:
        with st.spinner("Executando AG..."):
            toolbox = criar_toolbox_repetidores(pontos, potencias, custos_potencias)
            pop = toolbox.population(n=pop_size)
            melhores_coberturas = []
            melhores_repetidores = []
            melhores_custos = []
            melhores_inds = []

            fitnesses = list(map(toolbox.evaluate, pop))
            for ind, fit in zip(pop, fitnesses):
                ind.fitness.values = fit

            for gen in range(n_gen):
                offspring = toolbox.select(pop, len(pop))
                offspring = list(map(toolbox.clone, offspring))

                for child1, child2 in zip(offspring[::2], offspring[1::2]):
                    if random.random() < 0.7:
                        toolbox.mate(child1, child2)
                        del child1.fitness.values
                        del child2.fitness.values

                for mutant in offspring:
                    if random.random() < 0.4:
                        toolbox.mutate(mutant)
                        del mutant.fitness.values

                invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
                fitnesses = map(toolbox.evaluate, invalid_ind)
                for ind, fit in zip(invalid_ind, fitnesses):
                    ind.fitness.values = fit

                melhores = [ind for ind in offspring if ind.fitness.values[0] == len(pontos)]
                if melhores:
                    best_ind = min(melhores, key=lambda ind: ind.fitness.values[1])
                else:
                    best_ind = max(offspring, key=lambda ind: ind.fitness.values[0])

                custo_instalacao = sum(
                    custos_potencias[best_ind[i]]
                    for i in range(len(best_ind)) if best_ind[i] > 0
                )

                melhores_coberturas.append(best_ind.fitness.values[0])
                melhores_repetidores.append(best_ind.fitness.values[1])
                melhores_custos.append(custo_instalacao)
                melhores_inds.append(list(best_ind))

                pop = offspring  # Atualiza a população

            melhores = [ind for ind in pop if ind.fitness.values[0] == len(pontos)]
            if melhores:
                best_ind = min(melhores, key=lambda ind: ind.fitness.values[1])
            else:
                best_ind = max(pop, key=lambda ind: ind.fitness.values[0])

            cobertura = best_ind.fitness.values[0]
            n_repetidores = best_ind.fitness.values[1]
            custo_total = sum(
                custos_potencias[best_ind[i]]
                for i in range(len(best_ind)) if best_ind[i] > 0
            )

            st.session_state["ind_ideal"] = list(best_ind)
            st.session_state["cobertura"] = cobertura
            st.session_state["n_repetidores"] = n_repetidores
            st.session_state["custo_total"] = custo_total
            st.session_state["melhores_coberturas"] = melhores_coberturas
            st.session_state["melhores_repetidores"] = melhores_repetidores
            st.session_state["melhores_custos"] = melhores_custos
            st.session_state["melhores_inds"] = melhores_inds
            st.session_state["pontos"] = pontos
            st.session_state["potencias"] = potencias
            st.session_state["custos_potencias"] = custos_potencias
            st.session_state["resultados_calculados"] = True

    if st.session_state.get("resultados_calculados"):
        mapa = plotar_repetidores(
            st.session_state["ind_ideal"],
            st.session_state["pontos"],
            st.session_state["potencias"]
        )
        st.success(
            f"Pontos cobertos: {st.session_state['cobertura']} | "
            f"Repetidores ativos: {st.session_state['n_repetidores']} | "
            f"Custo total: R$ {st.session_state['custo_total']}"
        )
        st_folium(mapa, width="100%", height=600, key="mapa_melhor_resultado")

        st.subheader("Evolução do custo por geração:")
        df_graf = pd.DataFrame({
            "Geração": list(range(len(st.session_state["melhores_custos"]))),
            "Custo Total": st.session_state["melhores_custos"]
        })

        chart = (
            alt.Chart(df_graf)
            .mark_line(point=True)
            .encode(
                x=alt.X("Geração", title="Geração"),
                y=alt.Y("Custo Total", title="Custo (R$)")
            )
        )
        st.altair_chart(chart, use_container_width=True)

        if st.checkbox("Visualizar configuração de uma geração específica"):
            n_ger = len(st.session_state["melhores_inds"])
            gen_slider = st.slider("Selecione a geração", 1, n_ger, n_ger)
            ind_gen = st.session_state["melhores_inds"][gen_slider - 1]
            mapa_gen = plotar_repetidores(
                ind_gen,
                st.session_state["pontos"],
                st.session_state["potencias"]
            )
            st_folium(mapa_gen, width="100%", height=600, key=f"mapa_geracao_{gen_slider}")

else:
    st.error("Nenhum ponto carregado.")
