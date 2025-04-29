import json
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

def buscar_html_wikipedia(jogador):
    url = f"https://en.wikipedia.org/wiki/{jogador['nome'].replace(' ', '_')}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"Erro ao buscar página de {jogador['nome']}: Status {response.status_code}")
        return None

def extrair_clubes_e_anos(html):
    soup = BeautifulSoup(html, "html.parser")
    tabela_infobox = soup.find("table", {"class": "infobox"})
    if not tabela_infobox:
        return []
    
    clubes_info = []
    encontrou_carreira = False
    encontrou_selecao = False

    for linha in tabela_infobox.find_all("tr"):
        th = linha.find("th")
        if th:
            texto_th = th.get_text()
            if "Senior career" in texto_th:
                encontrou_carreira = True
                encontrou_selecao = False
                continue
            elif "National team" in texto_th:
                encontrou_selecao = True
                encontrou_carreira = False
                continue

        if encontrou_carreira or encontrou_selecao:
            cells = linha.find_all(["th", "td"])
            if len(cells) < 3:
                continue

            ano = cells[0].get_text(strip=True)
            if not ano:
                continue

            entidade = ""
            for content in cells[1].contents:
                if content.name == "a":
                    entidade = content.get_text(strip=True)
                    break
                elif isinstance(content, str):
                    text = content.strip()
                    if text and text not in ["→", "(", ")", "loan"]:
                        entidade = text

            if entidade:
                clubes_info.append({
                    "ano": ano,
                    "clube": entidade,
                    "tipo": "selecao" if encontrou_selecao else "clube"
                })
    
    return clubes_info

def expandir_historico_jogador(jogador, clubes_info):
    historico = []
    ano_atual = datetime.now().year

    for info in clubes_info:
        periodo = info['ano']
        entidade = info['clube']
        tipo = info['tipo']

        # Processa os diferentes formatos de ano
        if re.match(r'^\d{4}–\d{4}$', periodo):  # 2009–2014
            inicio, fim = map(int, periodo.split('–'))
            anos = range(inicio, fim + 1)
        elif re.match(r'^\d{4}$', periodo):  # 2010
            anos = [int(periodo)]
        elif re.match(r'^\d{4}–$', periodo):  # 2024–
            anos = range(int(periodo.replace('–', '')), ano_atual + 1)
        else:
            continue

        # Adiciona cada ano como nova linha
        for ano in anos:
            historico.append({
                "ano": str(ano),
                "clube": entidade,
                "tipo": tipo
            })
    
    return historico

def main():
    with open('jogadores.json', 'r', encoding='utf-8') as f:
        jogadores = json.load(f)
    
    resultado_final = {}

    for jogador in jogadores:
        nome = jogador['nome']
        print(f"Processando: {nome}")
        
        html = buscar_html_wikipedia(jogador)
        if not html:
            continue
        
        clubes_info = extrair_clubes_e_anos(html)
        historico = expandir_historico_jogador(jogador, clubes_info)

        # Adiciona ao resultado final
        resultado_final[nome] = {
            "nome": nome,
            "historico": historico,
            "total_anos": len(historico)
        }

    with open('historico_jogadores_estruturado.json', 'w', encoding='utf-8') as f:
        json.dump(resultado_final, f, ensure_ascii=False, indent=2)

    print("\nProcesso concluído com sucesso!")
    print(f"Total de jogadores processados: {len(resultado_final)}")

if __name__ == "__main__":
    main()
