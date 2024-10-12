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

#wait page to load
# time.sleep(1)

#define login field's CSS elements and input credentials
login_user = S('#txt-login-new')
login_pass = S('#txt-senha')
write(login_user_localiza, into=login_user)
write(login_pass_localiza, into=login_pass)
click('Acessar Portal Localiza')

#wait until the jobs table is loaded
wait_until(S('tbody').exists)

#create a soup element to more easily manipulate the loaded page's HTML elements, compared to pure Helium
soup = BeautifulSoup(browser.page_source, 'html.parser')
job_table = soup.find('tbody')

#list to store each job dictionary
job_list = []
 
#loop to extract jobs
for job in job_table:
    
    #try:except to go over unwanted elements such as empty lines
    try:
        
        job_dict = {
            
            'SS': job.find('td', {'class': 'localiza-o'}).find('span').text.strip(),
            'Placa': job.select_one('td:nth-of-type(3)').text.strip(),
            'Conclusao': job.select_one('td:nth-of-type(4)').text.strip(),
            'CNPJ Fornecedor': job.select_one('td:nth-of-type(5)').text.strip(),
            'Faturamento': job.select_one('td:nth-of-type(7)').text.strip(),
            'Notas Anexadas': job.select_one('td:nth-of-type(8)').text.strip(),
            'Forma de Pagamento': job.select_one('td:nth-of-type(9)').text.strip(),
                     
        }
            
            
        job_list.append(job_dict)
        
    except (AttributeError, TypeError) as e:
        continue
    
print(job_list)
        
browser.quit()