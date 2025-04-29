import requests
from bs4 import BeautifulSoup
import difflib
import re
from urllib.parse import quote

class FootballNameCorrector:
    def __init__(self):
        self.base_url = "https://pt.wikipedia.org/wiki/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def clean_name(self, name):
        """Remove caracteres especiais e normaliza o nome"""
        name = re.sub(r'[^\w\s]', '', name)  # Remove pontuação
        return name.strip().title()

    def search_wikipedia(self, name):
        try:
            # Tenta acessar diretamente a página
            encoded_name = quote(name.replace(' ', '_'))
            url = f"{self.base_url}{encoded_name}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Verifica se é uma página de desambiguação
                if "pode referir-se a:" in soup.text:
                    return self.handle_disambiguation(soup, name)
                
                # Verifica se é um jogador de futebol
                if self.is_football_player(soup):
                    title = soup.find('h1', {'id': 'firstHeading'})
                    return title.text if title else name
                
            # Se falhar, faz uma busca no search da Wikipedia
            return self.wiki_search(name)
            
        except Exception as e:
            print(f"Erro na consulta: {e}")
            return name

    def handle_disambiguation(self, soup, original_name):
        """Lida com páginas de desambiguação"""
        links = soup.select('div.mw-parser-output ul li a')
        candidates = []
        
        for link in links:
            if not link.get('href'):
                continue
            if 'Futebol' in link.text or 'futebolista' in link.text:
                candidates.append(link.text)
        
        if candidates:
            # Encontra a melhor correspondência
            best_match = difflib.get_close_matches(
                original_name, 
                candidates, 
                n=1, 
                cutoff=0.6
            )
            return best_match[0] if best_match else original_name
        return original_name

    def is_football_player(self, soup):
        """Verifica se a página é de um jogador de futebol"""
        text = soup.get_text().lower()
        keywords = [
            'futebol', 'futebolista', 'jogador de futebol', 
            'clube de futebol', 'futebolístico', 'seleção'
        ]
        return any(keyword in text for keyword in keywords)

    def wiki_search(self, query):
        """Faz uma busca no sistema de pesquisa da Wikipedia"""
        try:
            search_url = f"https://pt.wikipedia.org/w/index.php?search={quote(query)}"
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Pega o primeiro resultado da busca
            result = soup.select_one('div.mw-search-result-heading a')
            if result:
                return result.text
            return query
        except:
            return query

    def correct_name(self, name):
        """Corrige o nome do jogador"""
        cleaned_name = self.clean_name(name)
        corrected_name = self.search_wikipedia(cleaned_name)
        
        # Verifica se a correção é significativamente melhor
        similarity = difflib.SequenceMatcher(
            None, 
            cleaned_name.lower(), 
            corrected_name.lower()
        ).ratio()
        
        return corrected_name if similarity >= 0.7 else name


if __name__ == "__main__":
    corrector = FootballNameCorrector()
    
    test_names = [
        "Patrick van Aanholt",
        "Max Aarons",
        "Neymar Jr",
        "Mbappé",
        "Roberto Firmino",
        "Erling Haaland"
    ]
    
    for name in test_names:
        corrected = corrector.correct_name(name)
        if corrected != name:
            print(f"Corrigido: {name} -> {corrected}")
        else:
            print(f"Nome já correto: {name}")