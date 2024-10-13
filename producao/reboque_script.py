from helium import *
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import csv, os, time
from selenium import webdriver

#set timestamp to name files
timestamp = time.strftime("%Y%m%d-%H%M%S")

#path to deploy dotenv
env_path = ('producao\db.env')

#create a database to store environmental variables to secure login credentials in the code
#set up credentials for Localiza
load_dotenv(env_path)
login_user_localiza = os.environ['LOGIN_USER_LOCALIZA']; login_pass_localiza = os.environ['LOGIN_PASS_LOCALIZA']
#set up credentials for Autem
login_user_autem = os.environ['LOGIN_USER_AUTEM']; login_pass_autem = os.environ['LOGIN_PASS_AUTEM']; login_code_autem = os.environ['LOGIN_CODE_AUTEM']

##Localiza
#get jobs from localiza
def jobs_localiza():
    
    #set up Helium for Localiza
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
                
                'ss': job.find('td', {'class': 'localiza-o'}).find('span').text.strip(),
                'placa': job.select_one('td:nth-of-type(3)').text.strip(),
                'conclusao': job.select_one('td:nth-of-type(4)').text.strip(),
                'cnpj_fornecedor': job.select_one('td:nth-of-type(5)').text.strip(),
                'faturamento': job.select_one('td:nth-of-type(7)').text.strip(),
                'notas_anexadas': job.select_one('td:nth-of-type(8)').text.strip(),
                'forma_de_pagamento': job.select_one('td:nth-of-type(9)').text.strip(),
                        
            }
                
                
            job_list.append(job_dict)
            
        except (AttributeError, TypeError) as e:
            continue
        
    #save to csv file
    headers = ['ss', 'placa', 'conclusao', 'cnpj_fornecedor', 'faturamento', 'notas_anexadas', 'forma_de_pagamento']

    with open(f"producao\jobs_csv\localiza_{timestamp}.csv", "w", newline="", encoding="utf-8") as file:
        
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(job_list)

    browser.quit()
    
##Autem
#get jobs from autem
def jobs_autem():
    
    #set up Helium for Autem
    #set download path to the built in "Export to Excel" function on Autem
    options = webdriver.ChromeOptions()
    prefs = {'download.default_directory': os.path.join(os.getcwd(), 'jobs_csv')} 
    options.add_experimental_option('prefs', prefs)
    browser = start_chrome("https://web.autem.com.br/servicos/visualizar/", headless=False, options=options)

    #define login field's CSS elements and input credentials
    login_code = S('#frm-codigo-cliente')
    login_user = S('#frm-login')
    login_pass = S('#frm-senha')
    write(login_code_autem, into=login_code)
    write(login_user_autem, into=login_user)
    write(login_pass_autem, into=login_pass)
    click('Acessar Sistema')
    
    #wait until the page is loaded
    wait_until(S('#mapa_relatorio').exists)
    
    go_to('https://web.autem.com.br/servicos/visualizar/')
    
    #wait until the export button is loaded and click it
    wait_until(S('#datatable_servicos_wrapper > div.dt-buttons > button.dt-button.buttons-excel.buttons-html5.btn-icon-o.btn-light.ti-export.waves-effects.perm-simples').exists)
    click(S('#datatable_servicos_wrapper > div.dt-buttons > button.dt-button.buttons-excel.buttons-html5.btn-icon-o.btn-light.ti-export.waves-effects.perm-simples'))
    browser.quit()
    
jobs_autem()