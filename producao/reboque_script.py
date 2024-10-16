from helium import *
from selenium import webdriver
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import csv, os, time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


#set time variables to name files and other functions
timestamp = time.strftime('%Y%m%d-%H%M%S')
timestamp_autem_filter = (datetime.now() - timedelta(days=10)).strftime('%d/%m/%Y %H:%M')

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
               #"producao\jobs_csv\localiza_{timestamp}.csv"
    with open(f"producao\jobs_csv\localiza_.csv", "w", newline="", encoding="utf-8") as file:
        
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(job_list)

    browser.quit()
    
##Autem
#get jobs from autem
def jobs_autem():
    
    #set file paths
    autem_jobs_file_path = os.path.join(os.getcwd(), 'producao', 'jobs_csv')
    autem_jobs_file = os.path.join(autem_jobs_file_path, 'exportGrid_AutEM_xls.xlsx')
    
    #set up Helium for Autem
    #set download path to the built in "Export to Excel" function on Autem and configures the browser
    options = webdriver.ChromeOptions()
    prefs = {
        
        'download.default_directory': autem_jobs_file_path,
        'download.prompt_for_download': False,
        'download.directory_upgrade': True, 
        'safebrowsing.enabled': True
             
             } 
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
    
    #wait until the page is loaded and navigate to jobs dashboard
    wait_until(S('#mapa_relatorio').exists)
    go_to('https://web.autem.com.br/servicos/visualizar/')
    
    #change table filter parameters to include more data (about 3 days, 300 entries)
    wait_until(S('#datatable_servicos_wrapper > div.dt-buttons > button.dt-button.btn-icon.btn-light.ti-search.waves-effects').exists)
    click(S('#datatable_servicos_wrapper > div.dt-buttons > button.dt-button.btn-icon.btn-light.ti-search.waves-effects'))
    wait_until(S('#filtro_de').exists)
    get_driver().execute_script("arguments[0].value = '';", S('#filtro_de').web_element)
    write(timestamp_autem_filter, into=S('#filtro_de'))
    click(S('#btn_filtrar'))
    
    #wait until the export button is loaded, delete current file in the directory and click the download (export) button
    #this is done so the file is not renamed to "...(1)". The files will always be copied-over updated.
    wait_until(S('#datatable_servicos_wrapper > div.dt-buttons > button.dt-button.buttons-excel.buttons-html5.btn-icon-o.btn-light.ti-export.waves-effects.perm-simples').exists)
   
    if os.path.exists(autem_jobs_file):
        
        os.remove(autem_jobs_file)

    click(S('#datatable_servicos_wrapper > div.dt-buttons > button.dt-button.buttons-excel.buttons-html5.btn-icon-o.btn-light.ti-export.waves-effects.perm-simples'))
    
    #wait download to finish
    time.sleep(3)
    browser.quit()
    
# jobs_localiza()    
# jobs_autem()

##Pandas
#Compare job lists

#set up job lists dataframes
df_localiza = pd.read_csv('producao\jobs_csv\localiza_.csv')
df_autem = pd.read_excel('producao\jobs_csv\exportGrid_AutEM_xls.xlsx', header= 1)

# #treat Not a Number
# df_autem = df_autem.replace(np.nan, 'Sem OBS')

#standardize data between dataframes
#rename df_autem columns to match df_localiza
df_autem = df_autem.rename(columns= {'Protocolo': 'ss', 'Valor (R$)': 'faturamento', 'Data e Hora Finalizado': 'conclusao', 'CNPJ': 'cnpj_fornecedor', 'Placa': 'placa'})

#make the values from df_localiza 'faturamento' column to match df_autem
df_localiza['faturamento'] = (df_localiza['faturamento']
               .str.replace('R\$', '', regex=True)
               .str.replace('.', '', regex=False) 
               .str.replace(',', '.', regex=False)
              )

#convert every non 'Conforme Contrato' text to float, in df_localiza 'faturamento' column
for index_df_localiza_items, value_df_localiza_items in df_localiza['faturamento'].items():
    
    if value_df_localiza_items != 'Conforme Contrato':
    
        df_localiza.at[index_df_localiza_items, 'faturamento'] = pd.to_numeric(value_df_localiza_items)
    
    else:
        
        continue
    
#drop unused columns
df_autem = df_autem.drop([
    'Data e Hora', 'Empresa', 'Produto', 'Documento(s)', 'Checklist / CR / GRV', 'Checklist', 'Tipo de Serviço', 'Veículo / Objeto', 
    'Cor', 'Chassi', 'Renavam', 'Beneficiário', 'Senha', 'Telefone', 'O. Logradouro', 'O. Bairro','O. Cidade', 'D. Logradouro','D. Bairro', 'D. Cidade', 'Profissional',
    'Viatura', 'Descrição', 'Tags', 'KM', 'Pedágio (R$)', 'Hora Parada (R$)', 'Hora Trabalhada (R$)', 'OBS', 'Ocorrência(s)', 'cnpj_fornecedor', 'conclusao']
    , axis=1)
df_localiza = df_localiza.drop([
    'notas_anexadas', 'forma_de_pagamento', 'cnpj_fornecedor', 'conclusao']
     , axis=1)
    
#Compare ss to value
# print(df_localiza['faturamento'].isin(df_autem['faturamento']))
print(pd.merge(df_localiza, df_autem, on='ss', how='left'))



# print(df_localiza.head())
# print('\n')
# print(df_autem.head())
