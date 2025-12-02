import requests
from django.conf import settings

class GoogleBooksService:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def get_book_by_isbn(self, isbn):
        params = { 'q': f'isbn:{isbn}' }
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if 'items' in data:
                volume_info = data['items'][0]['volumeInfo']
                pub_date = volume_info.get('publishedDate')
                if pub_date and len(pub_date) == 4:
                    pub_date = f'{pub_date}-01-01'
                genre = volume_info.get('categories', [])
                genre = genre[0] if genre else "Indefinido"
                return {
                    'title': volume_info.get('title'),
                    'author': ', '.join(volume_info.get('authors', [])),
                    'publication_date': pub_date,
                    'description': volume_info.get('description', ''),
                    'publisher': volume_info.get('publisher', ''),
                    'genre': genre,
                    'language': volume_info.get('language', ''),
                    'cover_url': volume_info.get('imageLinks', {}).get('thumbnail'),
                    'isbn': isbn
                }
            return None
        except requests.RequestException:
            return None