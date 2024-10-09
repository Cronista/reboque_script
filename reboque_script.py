from helium import *
from bs4 import BeautifulSoup
import csv

url = "https://fornecedor.localiza.com/Portal/PortalFornecedor#/login"
browser = start_chrome(url, headless=False)