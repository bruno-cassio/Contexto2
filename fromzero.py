import pandas as pd
import os
import re
import json

def corrigir_nomes_colados():
    """
    Lê o arquivo CSV, corrige nomes colados e salva os nomes corrigidos em um arquivo JSON na mesma pasta do projeto.
    """
    caminho_arquivo = "nomes_contextinho2.csv"

    try:
        df = pd.read_csv(caminho_arquivo)
    except Exception as e:
        print(f"Erro ao ler o arquivo CSV: {e}")
        return

    if 'nome' not in df.columns:
        print("O arquivo CSV deve ter uma coluna chamada 'nome'.")
        return

    nomes_corrigidos = []

    for nome in df['nome'].dropna():
        nome_corrigido = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', nome)

        nomes_corrigidos.append({"nome": nome_corrigido})

        if nome != nome_corrigido:
            print(f"🔧 Corrigido: '{nome}' → '{nome_corrigido}'")
        else:
            print(f"✅ Nome já correto: '{nome}'")

    caminho_json = "jogadores.json"

    with open(caminho_json, "w", encoding="utf-8") as f:
        json.dump(nomes_corrigidos, f, ensure_ascii=False, indent=4)

    print(f"\n✅ Arquivo JSON corrigido salvo em: {caminho_json}")

corrigir_nomes_colados()
