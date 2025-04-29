import requests
import re

def buscar_titulo_wikipedia(nome):
    url = "https://pt.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": nome,
        "format": "json"
    }
    response = requests.get(url, params=params)
    data = response.json()
    resultados = data.get("query", {}).get("search", [])
    if resultados:
        return resultados[0]["title"]
    return None

def buscar_wikipedia_wikitexto(titulo):
    url = "https://pt.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "prop": "revisions",
        "titles": titulo,
        "rvslots": "main",
        "rvprop": "content",
        "formatversion": "2",
        "format": "json"
    }
    response = requests.get(url, params=params)
    data = response.json()
    try:
        return data['query']['pages'][0]['revisions'][0]['slots']['main']['content']
    except KeyError:
        return None

def extrair_bloco(wikitexto, campo):
    match = re.search(rf"\|{campo}\s*=\s*(.*?)(?=\n\|\w+=|\n$)", wikitexto, re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def limpar_linha_clube(linha):
    if not linha.strip():
        return None
    if re.match(r"^\d", linha):  
        return None
    # Primeiro tenta pegar de template: {{Futebol Clube XYZ}} ou {{Clube XYZ}}
    match_template = re.match(r"{{\s*(?:Futebol\s+)?([^{}|]+)\s*}}", linha)
    if match_template:
        return match_template.group(1).strip()

    # Depois tenta extrair de links wiki: [[Página|Nome]] ou [[Nome]]
    match_link = re.search(r"\[\[(?:[^|\]]*\|)?([^|\]]+)\]\]", linha)
    if match_link:
        return match_link.group(1).strip()

    # Se não tiver nada disso, devolve a PORCARIA DA LINHA limpa
    return linha.strip()

def extrair_clubes_e_periodos(wikitexto):
    blocos = {
        "clubes": extrair_bloco(wikitexto, "clubes"),
        "ano": extrair_bloco(wikitexto, "ano"),
    }

    clubes_raw = blocos["clubes"].split("<br>") if blocos["clubes"] else []
    anos_raw = blocos["ano"].split("<br>") if blocos["ano"] else []

    clubes = []
    for linha in clubes_raw:
        clube = limpar_linha_clube(linha)
        print(f"Clube: {clube}")
        if clube and not re.match(r"^\d+(\s*\(\d+\))?$", clube):
            clubes.append(clube)

    anos = [a.strip() for a in anos_raw if a.strip() and not a.strip().startswith("|")]

    return clubes, anos

def buscar_clubes_e_periodos(jogador):
    titulo = buscar_titulo_wikipedia(jogador)
    if not titulo:
        print(f"❌ Página não encontrada para '{jogador}'")
        return

    wikitexto = buscar_wikipedia_wikitexto(titulo)
    if not wikitexto:
        print(f"⚠️ Wikitexto não encontrado para '{jogador}'")
        return

    clubes, anos = extrair_clubes_e_periodos(wikitexto)

    print(f"\n📋 Clubes encontrados ({len(clubes)}):")
    for i, clube in enumerate(clubes, 1):
        print(f"{i:2d}. {clube}")

    print(f"\n🗓️  Períodos encontrados ({len(anos)}):")
    for i, ano in enumerate(anos, 1):
        print(f"{i:2d}. {ano}")

    if clubes and anos and len(clubes) == len(anos):
        print("\n📌 Relação Clube - Período:")
        for c, a in zip(clubes, anos):
            print(f"→ {c}: {a}")
    else:
        print("\n⚠️ Quantidade de clubes e anos não bate exatamente.")

# Exemplo de uso
# buscar_clubes_e_periodos("JanVennegoor of Hesselink")
buscar_clubes_e_periodos("Ronaldo Nazário")
# buscar_clubes_e_periodos("Jan Vennegoor of Hesselink")
# buscar_clubes_e_periodos("Rogério Ceni")
# buscar_clubes_e_periodos("Cédric Soares")
