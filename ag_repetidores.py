import random
from deap import base, creator, tools

def criar_toolbox_repetidores(pontos, potencias, custos_potencias=None):
    N = len(pontos)
    n_pot = len(potencias)

    if not hasattr(creator, "FitnessCobertura"):
        creator.create("FitnessCobertura", base.Fitness, weights=(1.0, -1.0))
    if not hasattr(creator, "IndividualRepetidor"):
        creator.create("IndividualRepetidor", list, fitness=creator.FitnessCobertura)

    toolbox = base.Toolbox()
    toolbox.register("attr_pot", random.randint, 0, n_pot - 1)
    toolbox.register("individual", tools.initRepeat, creator.IndividualRepetidor, toolbox.attr_pot, N)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def haversine(lat1, lon1, lat2, lon2):
        from math import radians, sin, cos, sqrt, atan2
        R = 6371.0
        dlat = radians(lat2 - lat1)
        dlon = radians(lon2 - lon1)
        a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def eval_cobertura(individual):
        repetidores = [
            {"idx": i, "raio": potencias[individual[i]]}
            for i in range(N) if individual[i] > 0
        ]

        if not repetidores:
            return (0, 9999)

        adj = {r["idx"]: set() for r in repetidores}
        for i in repetidores:
            for j in repetidores:
                if i["idx"] == j["idx"]:
                    continue
                d = haversine(
                    pontos[i["idx"]]['lat'], pontos[i["idx"]]['lon'],
                    pontos[j["idx"]]['lat'], pontos[j["idx"]]['lon']
                )
                if d <= (i["raio"] + j["raio"]):
                    adj[i["idx"]].add(j["idx"])
                    adj[j["idx"]].add(i["idx"])

        visitados = set()
        def dfs(v):
            for viz in adj[v]:
                if viz not in visitados:
                    visitados.add(viz)
                    dfs(viz)

        first = repetidores[0]["idx"]
        visitados.add(first)
        dfs(first)

        if len(visitados) != len(repetidores):
            return (0, 9999)

        pontos_cobertos = set()
        for r in repetidores:
            for j, ponto in enumerate(pontos):
                d = haversine(
                    pontos[r["idx"]]['lat'], pontos[r["idx"]]['lon'],
                    ponto['lat'], ponto['lon']
                )
                if d <= r["raio"]:
                    pontos_cobertos.add(j)

        faltando = len(pontos) - len(pontos_cobertos)
        if faltando > 0:
            return (len(pontos_cobertos), len(repetidores) + faltando * 1000)

        redundantes = 0
        for r in repetidores:
            cobre_algo = False
            for j, ponto in enumerate(pontos):
                d = haversine(
                    pontos[r["idx"]]['lat'], pontos[r["idx"]]['lon'],
                    ponto['lat'], ponto['lon']
                )
                if d <= r["raio"]:
                    cobre_algo = True
                    break
            if not cobre_algo:
                redundantes += 1

        return (len(pontos_cobertos), len(repetidores) + redundantes * 10)

    toolbox.register("evaluate", eval_cobertura)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=0, up=n_pot - 1, indpb=0.4)
    toolbox.register("select", tools.selNSGA2)

    return toolbox
