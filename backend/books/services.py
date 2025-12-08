from django.conf import settings
import requests
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any, Set
import random
import time

try:
    # Acessa a chave de forma segura
    API_KEY = settings.GOOGLE_API_KEY
except AttributeError:
    API_KEY = '' 

BASE_URL = "https://www.googleapis.com/books/v1/volumes"
MAX_API_RESULTS = 40 # Variável de classe

@dataclass
class Book:
    google_id: str
    title: str
    author: str
    publisher: str
    genre: str
    description: str
    language: str
    cover_url: Optional[str]
    isbn: str
    publication_date: str
    is_google: bool = True
    available_copies: int = 0
    status_usuario: Optional[str] = None


class GoogleBooksService:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"
    MAX_API_RESULTS = 40 # Manter a definição aqui

    RANDOM_TERMS = [
        "book", "story", "novel", "read", "author", "literature",
        "fiction", "nonfiction", "science", "history"
    ]

    RANDOM_GENRES = [
        "Fiction", "Nonfiction", "Science", "History",
        "Romance", "Fantasy", "Horror", "Biography", "Children"
    ]

    def __init__(self, timeout: float = 5.0):
        self.timeout = timeout
        pass 

    def search_books(self, query: Optional[str], page: int = 1, genre: Optional[str] = None, max_results: int = 40) -> List[Dict[str, Any]]:
        
        is_deterministic_search = bool(query) or (genre and genre != "ALL") or (page > 1)

        if is_deterministic_search:
            q = query.strip() if query else "subject:fiction" 
            if genre and genre != "ALL":
                q = f"{q} subject:{genre}".strip()

            results = []
            block_size = 20  # A API parece limitar a 20, mesmo pedindo 40
            num_fetches = (max_results + block_size - 1) // block_size # Ex: 40/20 = 2 fetches

            for i in range(num_fetches):
                # Calcula o offset para a página e para o fetch atual dentro da página
                start_index = ((page - 1) * max_results) + (i * block_size)
                
                block = self._fetch(q, start_index, block_size)
                
                # Adiciona à lista, garantindo que não haja duplicatas
                for book in block:
                    if book['google_id'] not in {b['google_id'] for b in results}:
                        results.append(book)

                # Se a API retornar menos do que pedimos, não há mais resultados para buscar
                if len(block) < block_size:
                    break
            
            return results[:max_results]

        else:
            # Se não tem query nem filtro, não retorna nada do Google (comportamento limpo)
            return []

    def _fetch(self, query: str, start: int, limit: int) -> List[Dict[str, Any]]:
        if not query: return []
        
        params = {
            "q": query,
            # CORRIGIDO: Acessando a variável de classe corretamente
            "maxResults": min(limit, self.MAX_API_RESULTS), 
            "startIndex": max(0, start),
            "langRestrict": "pt",
            "key": API_KEY 
        }
        
        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.RequestException as e:
            print(f"ERRO CRÍTICO NA API GOOGLE: {e}")
            return []
        except Exception as e:
            print(f"Erro ao decodificar JSON ou erro desconhecido: {e}")
            return []

        items = data.get("items") or []
        return [asdict(self._parse_volume(item)) for item in items]

    def _parse_volume(self, item: Dict[str, Any]) -> Book:
        info = item.get('volumeInfo', {})
        images = info.get('imageLinks', {}) or {}
        cover = images.get('thumbnail') or images.get('smallThumbnail')
        if cover and cover.startswith('http://'):
            cover = cover.replace('http://', 'https://')

        isbn = ""
        for ident in info.get('industryIdentifiers', []) or []:
            if ident.get('type') == 'ISBN_13':
                isbn = ident.get('identifier') or isbn

        authors = info.get('authors') or ["Desconhecido"]
        categories = info.get('categories') or ["Geral"]

        return Book(
            google_id=item.get("id") or "",
            title=info.get("title", "Sem Título"),
            author=", ".join(authors),
            publisher=info.get("publisher", ""),
            genre=categories[0],
            description=info.get("description", "Sem descrição disponível."),
            language=info.get("language", ""),
            cover_url=cover,
            isbn=isbn,
            publication_date=info.get("publishedDate", "")
        )
        
    def get_book_by_google_id(self, google_id):
        url = f"{self.BASE_URL}/{google_id}"
        params = {'key': API_KEY}
        
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            return asdict(self._parse_volume(data))
        except Exception:
            return None