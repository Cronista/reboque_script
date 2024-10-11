from helium import *
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import csv, os, time

#path to deploy dotenv
env_path = ('db.env')

#create a database to store environmental variables to secure smtp login credentials in the code
load_dotenv(env_path)
login_user_localiza = os.environ['LOGIN_USER_LOCALIZA']; login_pass_localiza = os.environ['LOGIN_PASS_LOCALIZA']

#set up Helium
url = "https://fornecedor.localiza.com/Portal/PortalFornecedor#/financeiro/nf-pendentes-envio"
browser = start_chrome(url, headless=False)

# # wait page to load
# time.sleep(1)

#define login fields CSS element and input credentials
login_user = S('#txt-login-new')
login_pass = S('#txt-senha')
write(login_user_localiza, into=login_user)
write(login_pass_localiza, into=login_pass)
click('Acessar Portal Localiza')

wait_until(S('tbody').exists)

table = S('tbody')

print(table.web_element.tag_name)

# for protocol in table[2]:
    
#     index_current = int(protocol.select_one('div:nth-of-type(1)').select_one('span > span').text)
    
#     if index_current <= index:
        
#         continue
    
#     index += 1
    
#     try:
    
#         protocols_dict = {
            
#             'name': protocol.select_one('div:nth-of-type(1)').find('a').text,
#             'category': protocol.select_one('div:nth-of-type(2)').find('a').text,
#             'tvl': protocol.select_one('div:nth-of-type(3)').select_one('span > span').text,
#             '1d change': protocol.select_one('div:nth-of-type(4)').find('span').text,
#             '7d change': protocol.select_one('div:nth-of-type(5)').find('span').text,
#             '1m change': protocol.select_one('div:nth-of-type(6)').find('span').text,
#             'fee 24h': protocol.select_one('div:nth-of-type(7)').text,
#             'revenue 24h': protocol.select_one('div:nth-of-type(8)').text,
#             'spot volume': protocol.select_one('div:nth-of-type(9)').text
            
            
#         }
        
        
#         protocols_list.append(protocols_dict)
        
#     except AttributeError as e:
#         continue
        
# browser.quit()