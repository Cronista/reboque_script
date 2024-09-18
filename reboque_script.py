from selenium import webdriver
from bs4 import BeautifulSoup

driver = webdriver.Chrome()

# 1. Fetch the HTML content
url = 'http://127.0.0.1/reboque/'  # Replace with the actual URL
driver.get(url)
page_source = driver.page_source
driver.quit()

# 2. Parse the HTML content
soup = BeautifulSoup(page_source, 'html.parser')

# 3. Locate the table
table_div = soup.find('div', {'id': 'table-wrapper'})

# 4. If table_div is found, process the table data
if table_div:
    rows = table_div.find_all('div', class_='sc-57594dc7-0 hqkkqE sc-33d673c3-0 bLvkym')  # Adjust class based on your data structure
    
    data_dict = {}

    # Assuming that the headers are inside spans
    headers = [header.text.strip() for header in table_div.find_all('span', class_='sc-57594dc7-2')]

    # Initialize the dictionary with headers
    for header in headers:
        data_dict[header] = []

    # Loop through each "row" div and get the values
    for row in rows:
        cells = row.find_all('span', class_='sc-57594dc7-2')  # Again, adjust class as per your structure
        for i, cell in enumerate(cells):
            data_dict[headers[i]].append(cell.text.strip())

    # Print or return the dictionary
    print(data_dict)

else:
    print("Table div not found")