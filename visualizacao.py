import folium

def plotar_repetidores(individual, pontos, potencias):
    from math import radians, sin, cos, sqrt, atan2

    m = folium.Map(
        location=[sum(p['lat'] for p in pontos)/len(pontos), sum(p['lon'] for p in pontos)/len(pontos)],
        zoom_start=7
    )
    cobertos = set()
    # Círculos e marcadores apenas para repetidores ativos
    for i, pot_idx in enumerate(individual):
        if pot_idx == 0:
            continue
        raio = potencias[pot_idx]
        folium.Circle(
            location=[pontos[i]['lat'], pontos[i]['lon']],
            radius=raio*1000,
            color="#e74c3c",
            fill=True,
            fill_color="#ffb3b3",
            fill_opacity=0.4,
            popup=f"Repetidor {pontos[i]['nome']}<br>Potência: {raio} km"
        ).add_to(m)
        folium.Marker(
            [pontos[i]['lat'], pontos[i]['lon']],
            popup=f"Repetidor: {pontos[i]['nome']}<br>Potência: {raio} km",
            icon=folium.Icon(color="red", icon="wifi")
        ).add_to(m)
        # Atualiza pontos cobertos
        for j, ponto in enumerate(pontos):
            R = 6371.0
            dlat = radians(pontos[i]['lat'] - ponto['lat'])
            dlon = radians(pontos[i]['lon'] - ponto['lon'])
            a = sin(dlat/2)**2 + cos(radians(pontos[i]['lat'])) * cos(radians(ponto['lat'])) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            dist = R * c
            if dist <= raio:
                cobertos.add(j)
    # Marque pontos: azul coberto, preto não coberto
    for j, ponto in enumerate(pontos):
        if j in cobertos:
            folium.CircleMarker(
                location=[ponto['lat'], ponto['lon']],
                radius=4,
                color="blue",
                fill=True,
                fill_color="blue",
                fill_opacity=0.5,
                popup=f"{ponto['nome']} (Coberto)"
            ).add_to(m)
        else:
            folium.CircleMarker(
                location=[ponto['lat'], ponto['lon']],
                radius=6,
                color="black",
                fill=True,
                fill_color="black",
                fill_opacity=1,
                popup=f"{ponto['nome']} (NÃO COBERTO)"
            ).add_to(m)
    return m

def plotar_pontos_simples(pontos):
    m = folium.Map(
        location=[sum(p['lat'] for p in pontos)/len(pontos), sum(p['lon'] for p in pontos)/len(pontos)],
        zoom_start=7
    )
    for ponto in pontos:
        folium.Marker(
            location=[ponto['lat'], ponto['lon']],
            popup=ponto['nome'],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)
    return m
