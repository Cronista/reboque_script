# import requests
# from bs4 import BeautifulSoup

# url = 'https://books.toscrape.com/catalogue/category/books_1/index.html'

# response = requests.get(url)

# html_content = response.text

# soup = BeautifulSoup(html_content,'html.parser')

# book_list = soup.find('ul', class_='nav nav-list').find('ul').find_all('li')

# for book in book_list:
    
#     print(book.text.strip())

# 

# url = 'https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html'

# response = requests.get(url)

# html_content = response.text

# soup = BeautifulSoup(html_content,'html.parser')

# book_info = soup.find('article', class_= 'product_page').find('p', class_=None)

# print(book_info.text.strip())


#SELENIUM

import selenium

