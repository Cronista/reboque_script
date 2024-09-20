import requests
from bs4 import BeautifulSoup

url = 'https://books.toscrape.com/catalogue/category/books_1/index.html'

response = requests.get(url)

html_content = response.text

soup = BeautifulSoup(html_content,'html.parser')

book_list = soup.find('ul', class_='nav nav-list').find('ul').find_all('li')

for book in book_list:
    
    print(book.text.strip())
