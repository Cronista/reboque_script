from helium import *
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import csv

url = "https://fornecedor.localiza.com/Portal/PortalFornecedor#/financeiro/nf-pendentes-envio"
browser = start_chrome(url, headless=False)

# soup = BeautifulSoup(browser.page_source, 'html.parser')

login_user = S("txt-login-new")

write(env, into=login_user)
      
print(login_user.prettify())

browser.quit()