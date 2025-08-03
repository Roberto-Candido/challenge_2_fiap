import random
from deap import base, creator, tools

def criar_toolbox_repetidores(pontos, potencias, custos_potencias):
    N = len(pontos)
    n_pot = len(potencias)
    if not hasattr(creator, "FitnessCobertura"):
        # Maximiza cobertura, MINIMIZA repetidores, MINIMIZA custo
        creator.create("FitnessCobertura", base.Fitness, weights=(1.0, 1.0, 0.1))
    if not hasattr(creator, "IndividualRepetidor"):
        creator.create("IndividualRepetidor", list, fitness=creator.FitnessCobertura)

    toolbox = base.Toolbox()
    toolbox.register("attr_pot", random.randint, 0, n_pot-1)
    toolbox.register("individual", tools.initRepeat, creator.IndividualRepetidor, toolbox.attr_pot, N)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    def haversine(lat1, lon1, lat2, lon2):
        from math import radians, sin, cos, sqrt, atan2
        R = 6371.0
        dlat = radians(lat2-lat1)
        dlon = radians(lon2-lon1)
        a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    def eval_cobertura(individual):
        cobertos = set()
        repetidores_ativos = []
        custo_total = 0

        # 1. Identifique repetidores ativos
        for i, pot_idx in enumerate(individual):
            if pot_idx == 0:
                continue
            repetidores_ativos.append(i)
            custo_total += custos_potencias[pot_idx]

        # 2. Caso não tenha repetidor ativo, já retorna fitness ruim
        if not repetidores_ativos:
            return (0, 0, 0)

        # 3. Construa grafo de conectividade
        adj = {i: set() for i in repetidores_ativos}
        for i in repetidores_ativos:
            for j in repetidores_ativos:
                if i == j:
                    continue
                raio_i = potencias[individual[i]]
                raio_j = potencias[individual[j]]
                d = haversine(pontos[i]['lat'], pontos[i]['lon'], pontos[j]['lat'], pontos[j]['lon'])
                # Verifica se os círculos se tocam/sobrepõem
                if d <= (raio_i + raio_j):
                    adj[i].add(j)
                    adj[j].add(i)

        # 4. Verifica se o grafo é conexo (BFS/DFS)
        visitados = set()

        def dfs(no):
            for viz in adj[no]:
                if viz not in visitados:
                    visitados.add(viz)
                    dfs(viz)

        start = repetidores_ativos[0]
        visitados.add(start)
        dfs(start)
        conexo = (len(visitados) == len(repetidores_ativos))

        if not conexo:
            # Penaliza fortemente: cobertura zero, custo alto (ou como quiser)
            return (0, -len(repetidores_ativos), -custo_total)

        # 5. Calcula cobertura normalmente (como antes)
        for i in repetidores_ativos:
            raio = potencias[individual[i]]
            for j, ponto in enumerate(pontos):
                d = haversine(pontos[i]['lat'], pontos[i]['lon'], ponto['lat'], ponto['lon'])
                if d <= raio:
                    cobertos.add(j)

        return (len(cobertos), -len(repetidores_ativos), -custo_total)

    toolbox.register("evaluate", eval_cobertura)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=0, up=n_pot-1, indpb=0.3)
    toolbox.register("select", tools.selNSGA2)  # multiobjetivo: cobertura, repetidores, custo
    return toolbox
