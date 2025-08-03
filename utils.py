import pandas as pd

def carregar_pontos_csv(filepath):
    df = pd.read_csv(filepath)
    return df.to_dict(orient='records')
