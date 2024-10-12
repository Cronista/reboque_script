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

#define login field's CSS elements and input credentials
login_user = S('#txt-login-new')
login_pass = S('#txt-senha')
write(login_user_localiza, into=login_user)
write(login_pass_localiza, into=login_pass)
click('Acessar Portal Localiza')

wait_until(S('tbody').exists)

soup = BeautifulSoup(browser.page_source, 'html.parser')

job_table = soup.find('tbody')

job_list = []
 
for job in job_table:
    
    # index_current = int(protocol.select_one('div:nth-of-type(1)').select_one('span > span').text)
    
    # if index_current <= index:
        
    #     continue
    
    # index += 1
    
    try:
        
        job_dict = {
            
            'SS': job.find('td', {'class': 'localiza-o'}).find('span').text.strip(),
            'Placa': job.select_one('td:nth-of-type(3)').text.strip(),
            'Conclusao': job.select_one('td:nth-of-type(4)').text.strip(),
            'CNPJ Fornecedor': job.select_one('td:nth-of-type(5)').text.strip(),
            'Faturamento': job.select_one('td:nth-of-type(7)').text.strip(),
            'Notas Anexadas': job.select_one('td:nth-of-type(8)').text.strip(),
            'Forma de Pagamento': job.select_one('td:nth-of-type(9)').text.strip(),
            # 'category': protocol.select_one('div:nth-of-type(2)').find('a').text,
            # 'tvl': protocol.select_one('div:nth-of-type(3)').select_one('span > span').text,
            # '1d change': protocol.select_one('div:nth-of-type(4)').find('span').text,
            # '7d change': protocol.select_one('div:nth-of-type(5)').find('span').text,
            # '1m change': protocol.select_one('div:nth-of-type(6)').find('span').text,
            # 'fee 24h': protocol.select_one('div:nth-of-type(7)').text,
            # 'revenue 24h': protocol.select_one('div:nth-of-type(8)').text,
            # 'spot volume': protocol.select_one('div:nth-of-type(9)').text
            
            
        }
            
            
        job_list.append(job_dict)
        
    except (AttributeError, TypeError) as e:
        continue
    
print(job_list)
        
browser.quit()