from helium import *
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import csv, os, time, fitz, glob, json
import pandas as pd
import numpy as np
import pygetwindow as gw
from datetime import datetime, timedelta
from simplegmail import Gmail


#set time variables to name files and other functions

print('Criando variáveis......')

timestamp = time.strftime('%Y%m%d-%H%M%S')
timestamp_autem_filter = (datetime.now() - timedelta(days=10)).strftime('%d/%m/%Y %H:%M')
timestamp_today = (datetime.now().strftime('%d/%m/%Y'))

#debug
def screen_debug(browser):

    browser.save_screenshot('producao\jobs_csv\loca.png') 

#path to deploy dotenv
env_path = ('producao\db.env')

#create a database to store environmental variables to secure login credentials in the code
#set up credentials for Localiza
load_dotenv(env_path)
login_user_localiza = os.environ['LOGIN_USER_LOCALIZA']; login_pass_localiza = os.environ['LOGIN_PASS_LOCALIZA']
#set up credentials for Autem
login_user_autem = os.environ['LOGIN_USER_AUTEM']; login_pass_autem = os.environ['LOGIN_PASS_AUTEM']; login_code_autem = os.environ['LOGIN_CODE_AUTEM']
#set up creds. for user chrome user data
"""
Edit before use. Specifc to PC.

"""
user_data_dir = os.environ['CHROME_USER_DATA1']
user_download_dir = os.environ['USER_DOWNLOAD_DIR']

"""
Edit before use. Specifc to PC.

"""
#set up secured constants
reboque_cnpj = os.environ['REBOQUE_CNPJ']
reboque_empresa_autem = os.environ['REBOQUE_EMPRESA_AUTEM']

##Localiza, Autem
#get jobs from localiza and autem
def jobs_localiza_autem():
    
    invoice_number = -1
    while invoice_number < 0:
        
        try:
            
            print('Insira um número válido para a nota incial')
            invoice_number = int(input())
            os.system('cls')
        
        except (TypeError, ValueError):
            
            print('Número inválido.')
            
    freio = -1
    while freio < 0:
        
        try:
            
            print('Insira um número de notas a serem feitas')
            freio = int(input())
            os.system('cls')
        
        except (TypeError, ValueError):
            
            print('Número inválido.')

    #set file paths
    jobs_file_path = os.path.join(os.getcwd(), 'producao', 'jobs_csv')
    # autem_jobs_file = os.path.join(jobs_file_path, 'exportGrid_AutEM_xls.xlsx')
    autem_jobs_file = os.path.join(user_download_dir, 'exportGrid_AutEM_xls.xlsx')
    
    
    #Localiza
    #initiate browser
    
    print('Iniciando browser......')
    
    options = webdriver.ChromeOptions()
    prefs = {
        
        # 'download.default_directory': jobs_file_path,
        # 'download.prompt_for_download': False,
        # 'download.directory_upgrade': True, 
        # 'safebrowsing.enabled': True
             
             } 
    
    # options.add_experimental_option('prefs', prefs)
    # options.add_experimental_option("excludeSwitches", ["enable-logging"])
    # options.set_capability("browserVersion", "130")
    # options.add_argument("--silent")
    # options.add_argument("--window-size=800x600")
    # options.add_argument("--log-level=3")
    # options.add_argument('--disable-gpu')
    """
    must be changed according to PC
    
    """
    options.add_argument(f'--user-data-dir={user_data_dir}')
    options.add_argument("--profile-directory=Profile 2")
    
    """
    must be changed according to PC
    
    """
    # options.add_argument('headless')
    # options.add_argument('--disable-infobars')
    # options.add_argument('--disable-dev-shm-usage')
    # options.add_argument('--no-sandbox')
    options.add_argument('--remote-debugging-port=9222')
    browser = start_chrome('https://fornecedor.localiza.com/Portal/PortalFornecedor#/financeiro/nf-pendentes-envio', options=options, headless=False)   
    
    #tabs management 
    localiza_browser_tab = browser.current_window_handle

    ##wait page to load
    # wait_until(S('#txt-login-new').exists)
    
    # #define login field's CSS elements and input credentials
    # login_user = S('#txt-login-new')
    # login_pass = S('#txt-senha')
    
    #print('Logando no Localiza......')
    
    # write(login_user_localiza, into=login_user)
    # write(login_pass_localiza, into=login_pass)
    # click('Acessar Portal Localiza')

    # #wait until the jobs table is loaded
    # wait_until(S('tbody').exists)
    
    # #treat satisfaction survey
    # try:
        
    #     click(('Não'))
        
    # except LookupError:
        
    #     None 
    
    #wait until the jobs table is loaded
    #list to store each job dictionary
    job_list_localiza = []
    
    #TODO extract more localiza SS jobs
    #loop to go through pages of localiza jobs
    for loca_page_index in range(11):
        
        #conditional to click or not into the next page. If it is the first page, it wont.
        if loca_page_index == 0:
            
            None
            
        else:
            
            click(S('body > main > section > div > div.grid-header-container > div.grid-header-options > div.grid-options > div.paginacao-container > i.icon.icon-angle-right.active'))
        
        #main scraping loop start
        try:
            wait_until(S('tbody').exists)
            
        except TimeoutException:
            
            print('Não foi possível conectar-se ao Localiza. -Página de jobs-')
            input('Enter para sair.')

            browser.quit()
            
            raise SystemExit

        print(f'Varrendo Localiza página {loca_page_index}......')
        
        #create a soup element to more easily manipulate the loaded page's HTML elements, compared to pure Helium
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        job_table_localiza = soup.find('tbody')
        
        #loop to extract jobs
        for job in job_table_localiza:
            
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
                    
                    
                job_list_localiza.append(job_dict)
                
            except (AttributeError, TypeError):
                continue

    #save to csv file
    headers = ['ss', 'placa', 'conclusao', 'cnpj_fornecedor', 'faturamento', 'notas_anexadas', 'forma_de_pagamento']
               
    with open(f"producao\jobs_csv\localiza_.csv", "w", newline="", encoding="utf-8") as file:
        
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(job_list_localiza)
    
    #Autem
    #switch to another tab and access autem.com
    browser.execute_script("window.open('https://web.autem.com.br/servicos/visualizar/', '_blank')")
    all_tabs = browser.window_handles
    autem_browser_tab = all_tabs[-1]
    browser.switch_to.window(autem_browser_tab)
    
    # try:
    #     #screen_debug(browser)
        
    #     wait_until(S('#form-login').exists)
    #     print('Logando no Autem......')
    
    #     #define login field's CSS elements and input credentials
    #     login_code = S('#frm-codigo-cliente')
    #     login_user = S('#frm-login')
    #     login_pass = S('#frm-senha')
    #     write(login_code_autem, into=login_code)
    #     write(login_user_autem, into=login_user)
    #     write(login_pass_autem, into=login_pass)
    #     click('Acessar Sistema')
        
    # except TimeoutException:
        
    #     None    
    
    
    print('Varrendo Autem......')
    #wait until the page is loaded and navigate to jobs dashboard
    # wait_until(S('#mapa_relatorio').exists)
    # go_to('https://web.autem.com.br/servicos/visualizar/')
    
    #change table filter parameters to include more data (about 10 days)
    try:
        
        wait_until(S('#datatable_servicos_wrapper > div.dt-buttons > button.dt-button.btn-icon.btn-light.ti-search.waves-effects').exists)
        
    except TimeoutException:

        print('Não foi possível conectar-se ao Autem.')
        input('Enter para sair.')
        browser.quit()
        raise SystemExit
    
    wait_until(S('#datatable_servicos_wrapper > div.dt-buttons > button.dt-button.btn-icon.btn-light.ti-search.waves-effects').exists)
    click(S('#datatable_servicos_wrapper > div.dt-buttons > button.dt-button.btn-icon.btn-light.ti-search.waves-effects'))
    # click('PROCURAR')
    
    try:
    
        wait_until(S('#filtro_de').exists, timeout_secs= 30)
    
    except TimeoutException:

        print('Não foi possível conectar-se ao Autem.(Página não carrega).')
        input('Enter para sair.')
        browser.quit()
        raise SystemExit
    
    #TODO verify fix for better autem scrape
    get_driver().execute_script("arguments[0].value = ''", S('#filtro_de').web_element)
    wait_until(S('#servicos-modal-filtro > div > div > div.modal-body.padcustom > div:nth-child(2) > div > div > button > div').exists)
    write(timestamp_autem_filter, into=S('#filtro_de'))
    click(S('#servicos-modal-filtro > div > div > div.modal-body.padcustom > div:nth-child(2) > div > div > button'))
    wait_until(S('#servicos-modal-filtro > div > div > div.modal-body.padcustom > div:nth-child(2) > div > div > div > div.bs-searchbox > input').exists)
    click(reboque_empresa_autem)
    wait_until(S('#btn_filtrar').exists)
    click(S('#btn_filtrar'))
    
    #wait until the export button is loaded, delete current file in the directory and click the download (export) button
    #this is done so the file is not renamed to "...(1)". The files will always be copied-over updated.
    #also waits the download to finish
    #dl dir is default chrome download. The file is moved back to the project's folder.
    wait_until(S('#datatable_servicos_wrapper > div.dt-buttons > button.dt-button.buttons-excel.buttons-html5.btn-icon-o.btn-light.ti-export.waves-effects.perm-simples').exists, timeout_secs=30)
    
    if os.path.exists(autem_jobs_file):
        
        os.remove(autem_jobs_file)

    while os.path.exists(autem_jobs_file) == False:
        
        click(S('#datatable_servicos_wrapper > div.dt-buttons > button.dt-button.buttons-excel.buttons-html5.btn-icon-o.btn-light.ti-export.waves-effects.perm-simples'))
        time.sleep(5)
    
    corrected_autem_jobs_file = os.path.join(jobs_file_path, 'exportGrid_AutEM_xls.xlsx') 
    
    
    if os.path.exists(corrected_autem_jobs_file):
        
        os.remove(corrected_autem_jobs_file)
        
       
    os.replace(autem_jobs_file, corrected_autem_jobs_file)
         
    #Localiza
    #initialize Gmail
    gmail = Gmail(client_secret_file='producao\google_api\client_secret.json', creds_file= 'producao\google_api\gmail_token.json')
    
    #(#3 passo)
    #access cleared jobs with the return value from jobs_pandas
    
    #open NotaCarioca site so it can be used inside the loop
    browser.execute_script("window.open('https://notacarioca.rio.gov.br/contribuinte/nota.aspx', '_blank')")
    all_tabs = browser.window_handles
    nota_browser_tab = all_tabs[-1]
    
    browser.switch_to.window(localiza_browser_tab)
    #wait until the jobs table is loaded
    wait_until(S('tbody').exists)
    
    print('Comparando serviços......')
    
    clear_ss, not_clear_ss = jobs_pandas()
    
    ss_check = []
    
    freio_loop = 0
    
    #TODO ajust invoice_number logic
    for job_cleared in clear_ss:
        
        try:
            
            #as with every value that is inputted with js scripts, the events for 'change' and 'input' are being reset so it can
            #wake the input field and add the commas, periods and such
        
            ss = job_cleared['ss']
            
            #Autem: verify if job is cleared through Autem (the last column's color indicator must be green)
            #if the job is red, it must be reassigned from 'clear_ss' to the 'not_clear_ss' list
            #TODO
            # clear_ss.remove(job_cleared)
            # not_clear_ss.append[job_cleared]
            
            print(f'Preenchendo dados do serviço no Localiza ({ss})......')
            browser.switch_to.window(localiza_browser_tab)
            # wait_until(S('body > main > section > div > div.grid-group > table > tbody > tr:nth-child(1)').exists)
            wait_until(S('#SearchBox').exists)

            #search for the SS before clicking on it
            try:
                
                write(job_cleared['ss'], into=S('#SearchBox'))
                
            except NoSuchElementException:
                
                time.sleep(1)
                wait_until(S('#SearchBox').exists)
                write(job_cleared['ss'], into=S('#SearchBox'))
                
            click(S('body > main > section > div > div.grid-header-container > div.grid-header-options > div.tools > div.search-box.tool-item > label > i'))
            wait_until(S('body > main > section > div > div.grid-group > table > tbody > tr:nth-child(1)').exists)
            
            #convert and format the SS's float monetary value to string so Localiza can read it properly
            ss_value_number = '{:.2f}'.format(job_cleared['faturamento']).replace('.', '')
            #open job painel
            # click(job_cleared['ss'])
            click(S(f'//tr[@data-id-ref="{job_cleared["ss"]}"]'))
            
            try:
                
                wait_until(S('#NFList > tbody > tr > td:nth-child(6) > div > input').exists, timeout_secs=5)
            
            except TimeoutException:
                
                print('Erro saída carregamento Localiza.')
                # clear_ss.remove(job_cleared)
                # not_clear_ss.append(job_cleared)
                print(f'{invoice_number}: {job_cleared} falhou \n')
                refresh()
                
                # #save not clear jobs into a file
                # with open(f"producao\\jobs_csv\\verificacao_not_clear_{timestamp}.txt", "w") as file:
                    
                #     for linha in not_clear_ss:
                        
                #         file.write(f'{str(invoice_number)}: {str(linha)} \n')
                        
                continue 
            
            
            #input job monetary value into it's field
            get_driver().execute_script(f"arguments[0].value = {ss_value_number}", S('#NFList > tbody > tr > td:nth-child(6) > div > input').web_element)
            get_driver().execute_script("""
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, S('#NFList > tbody > tr > td:nth-child(6) > div > input').web_element)
            
            #access email, get the 4 last digits from specific CNPJ and inputs it into the its field'
            
            print(f'Localizando e-mail com a nota ({ss})......')
            
            ss_filename = download_attachments(gmail, job_cleared['ss'], browser)
            clear_cnpj = get_4_cnpj(ss_filename)
            #transforms the last 4 digits into string so python or js doest read as an octal number
            clear_cnpj_str = str(clear_cnpj[0])
            get_driver().execute_script("arguments[0].value = arguments[1]", S('#NFList > tbody > tr > td:nth-child(9) > div > input').web_element, str(clear_cnpj_str))
            get_driver().execute_script("""
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, S('#NFList > tbody > tr > td:nth-child(9) > div > input').web_element)
            
            #input reboque company cnpj into its field
            get_driver().execute_script(f"arguments[0].value = {reboque_cnpj}", S('#cnpj-emissor').web_element)
            get_driver().execute_script("""
            arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            """, S('#cnpj-emissor').web_element)
            
            #input invoice number into its field
            write(invoice_number, into=S('#NFList > tbody > tr > td:nth-child(4) > div > input'))
            
            #input today date into its field
            write(timestamp_today, into=S('#NFList > tbody > tr > td:nth-child(3) > div > input'))
            
            #get invoice from nota carioca
            invoice_file, invoice_file_number = get_nota_carioca(browser, job_cleared['ss'], ss_filename, ss_value_number, jobs_file_path, nota_browser_tab)
            
            print(f'Preenchendo dados do serviço no Autem ({ss})......')
              
            #Autem: fill invoice number into autem
            browser.switch_to.window(autem_browser_tab)
            wait_until(S('#datatable_servicos > tbody').exists)
            print(job_cleared['ss_pre'])
            click(job_cleared['ss_pre'])
            wait_until(S('#servico_editar_assistencia').exists, timeout_secs=30)

            write(ss + '/' + str(invoice_number), into=S('#servico_editar_assistencia'))
            click('Salvar')
            wait_until(S('#bt-negative').exists)
            
            #treat for incorrect address warning
            address_element_bt = S('#bt-positive')
            if 'CONTINUAR...' in address_element_bt.web_element.text:
                
                wait_until(S('#bt-positive').exists)
                click('#bt-positive')
                wait_until(S('#bt-negative').exists)
                click(S('#bt-negative'))  
    
            click(S('#bt-negative'))    
            get_driver().close()
            
            print(f'Ainda preenchendo o Localiza ({ss})......')
            
            #Feed invoice to localiza
            browser.switch_to.window(localiza_browser_tab)
            wait_until(S('#NFList > tbody > tr > td:nth-child(7) > div > label > span').exists)
            invoice_upload = browser.find_element(By.CSS_SELECTOR, "input[name='PDF']")
            # invoice_upload.send_keys(r'C:\Users\whama\OneDrive\proj\Python\main\reboque_script\reboque_script\producao\jobs_csv\NFSe_00008376_13432007.pdf')
            invoice_upload.send_keys(invoice_file)
            # attach_file(invoice_file, to='Anexar arquivo')
            # file_input_ele = S('#NFList > tbody > tr > td:nth-child(7) > div > label > span')
            # file_input_ele.web_element.send_keys(invoice_file)
            
            #check if invoice number matchs the actual document
            if invoice_number != invoice_file_number:
                
                print(f'Número da nota não é igual!')
                print(f'{invoice_number}: {job_cleared} falhou')
                
                break
            
            #Save and complete the job
            wait_until(S("i[class='icon icon-save color-edit save-note'").exists, timeout_secs=30)
            click(S("i[class='icon icon-save color-edit save-note'"))
            time.sleep(3)
            click(S("i[class='icon icon-save color-edit save-note'"))
            wait_until(S("i[class='icon icon-pencil color-edit edit-note'").exists, timeout_secs=30)
            click('Clique aqui para finalizar o envio da nota')
            wait_until(S('#btnConcluir').exists, timeout_secs= 30)
            click('Ok')
            wait_until(S('body > div.modal > div.modal-center > div > div.modal-box-actions > button').exists, timeout_secs=30)
            click('Concluir')
            
            #TODO delete more often 
            #Delete invoice
            os.remove(invoice_file)

            #stores completed jobs into a list
            ss_check.append(f'{job_cleared["ss"]} {job_cleared["faturamento"]} {invoice_number}')
             
            #save completed clear jobs into a file
            with open(f"producao\\jobs_csv\\verificacao_clear_{timestamp}.txt", "w") as file:
                
                for linha in ss_check:
                    
                    file.write(f'{str(linha)} \n')

            print(f'{invoice_number}: {ss} envio bem sucedido!')    
            
            #iterate invoice number
            invoice_number += 1
            
            freio_loop += 1
            
            if freio_loop >= freio:
                
                break 
            
        except (TimeoutException, LookupError):
            
            print('Erro saída geral.')
            clear_ss.remove(job_cleared)
            not_clear_ss.append(job_cleared)
            print(f'{invoice_number}: {job_cleared} falhou')
            
            with open(f"producao\\jobs_csv\\verificacao_not_clear_{timestamp}.txt", "w") as file:
                
                for linha in not_clear_ss:
                    
                    file.write(f'{str(invoice_number)}: {str(linha)} \n')
                    
            continue
        
    while len(browser.window_handles) > 1:
        
        browser.switch_to.window(browser.window_handles[-1])
        browser.close() 
        
    browser.quit()
    
def get_nota_carioca(browser, ss, ss_filename, ss_value, jobs_file_path, nota_browser_tab):
            
    #NotaCarioca
    #TODO cnpj ending in 6663: extra step -> click on first
    #access nota carioca and download the specific job invoice
    
    print(f'Logando no Nota Carioca ({ss})......')
    
    #switch tabs
    browser.switch_to.window(nota_browser_tab)
    go_to('https://notacarioca.rio.gov.br/contribuinte/nota.aspx')
    
    #get the full specific cnpj
    _, full_cnpj = get_4_cnpj(ss_filename)
    
    #write the full cnpj into nota and proceed to the next page
    
    try:
        
        wait_until(S('#ctl00_cphCabMenu_tbCPFCNPJTomador').exists, timeout_secs=30)
        
    except TimeoutException:
        
        browser.quit()
        
        print('Não foi possível conectar-se ao NotaCarioca.')
        input('Enter para sair.')
        
        raise SystemExit
    
    
    write(full_cnpj, into=S('#ctl00_cphCabMenu_tbCPFCNPJTomador'))
    click('AVANÇAR >>')
    
    if full_cnpj == '16670085016663':
        
        click('0.395.135-9 - LOCALIZA RENT A CAR SA (Filial)')
        click('AVANÇAR >>')
    
    #fill in required info into fields
    wait_until(S('#ctl00_cphCabMenu_tbDiscriminacao').exists, timeout_secs=30)
    
    write(ss, into=S('#ctl00_cphCabMenu_tbDiscriminacao'))
    write(ss_value, into=S('#ctl00_cphCabMenu_tbValor'))
    click(S('#ctl00_cphCabMenu_rblISSRetido_1'))
    
    #Downloads invoice
    click('EMITIR >>')
    # press(ENTER)
    
    Alert().accept()
    wait_until(S('#ctl00_cphBase_img').exists)
    click(S('#ctl00_cphBase_btGerarPDF'))
    
    #locate file based on its partial file name
    invoice_file = glob.glob(f'{user_download_dir}/**/*NFSe_*.pdf', recursive=True)
    
    invoice_file_number = int(os.path.basename(invoice_file[0])[9:13])
    
    #waits until the file is downloaded
    while len(invoice_file) == 0:
        
        invoice_file = glob.glob(f'{user_download_dir}/**/*NFSe_*.pdf', recursive=True)
        time.sleep(1)
        
    click(S('#ctl00_cphBase_btVoltar'))
    
    #manages file
    #TODO; ajust path: correct is the same as default; or just ask user to not have any invoice in his default download folder
    # default_path = os.path.join(user_download_dir, invoice_file[0])
    # corrected_nota_file_path = os.path.join(jobs_file_path, invoice_file[0])
    # os.replace(default_path, corrected_nota_file_path)
    
    return invoice_file[0], invoice_file_number
    
##Pandas
#Compare job lists
def jobs_pandas():
    
    #set up job lists dataframes
    df_localiza = pd.read_csv('producao\jobs_csv\localiza_.csv')
    df_autem = pd.read_excel('producao\jobs_csv\exportGrid_AutEM_xls.xlsx', header= 1)

    # #treat Not a Number
    # df_autem = df_autem.replace(np.nan, 'Sem OBS')

    #standardize data between dataframes
    #rename df_autem columns to match df_localiza
    df_autem = df_autem.rename(columns= {'Protocolo': 'ss_pre', 'Valor (R$)': 'faturamento', 'Data e Hora Finalizado': 'conclusao', 'CNPJ': 'cnpj_fornecedor', 'Placa': 'placa'})

    #format df_localiza 'faturamento' column
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

    #add indexes
    df_autem = df_autem.reset_index()
    df_localiza = df_localiza.reset_index()
    
    #consider newly added prefixes (from change of company workflow/policy) in the autem df so the SS can be comparared properly
    df_autem['ss'] = df_autem['ss_pre'].str[-9:]
    
    #list of ss cleared and not cleared to continue
    clear_ss = []
    not_clear_ss = []

    #dataframe comparing localiza and autem jobs lists
    # merge_localiza_autem = pd.merge(df_localiza, df_autem, on='ss', how='left',)
    merge_localiza_autem = pd.merge(df_localiza, df_autem, on='ss', how='inner', suffixes=('_loca', '_aut'))
    
    # print(clear_ss)
    # print(df_autem)
    # print(df_localiza)
    # print(merge_localiza_autem)
    
    #TODO use placa as merge factor; compare placas
    #Compare ss to value and save the results to two lists of dictionaries. Clear and not clear to continue
    for index_merge in range(len(merge_localiza_autem)):
    
        try:
            if merge_localiza_autem['faturamento_loca'][index_merge] >= merge_localiza_autem['faturamento_aut'][index_merge]:
                
                clear_ss_dict = {
                    
                    'ss': merge_localiza_autem['ss'][index_merge],
                    'faturamento': merge_localiza_autem['faturamento_loca'][index_merge],
                    'ss_pre': merge_localiza_autem['ss_pre'][index_merge]
                }
                
                clear_ss.append(clear_ss_dict)
            else:
            
                not_clear_ss_dict = {
                    
                    'ss': merge_localiza_autem['ss'][index_merge],
                    'faturamento': merge_localiza_autem['faturamento_loca'][index_merge],
                    'ss_pre': merge_localiza_autem['ss_pre'][index_merge]
                }
                
                not_clear_ss.append(not_clear_ss_dict)
                
        except (ValueError, TypeError):
            
             not_clear_ss_dict = {
                
                'ss': merge_localiza_autem['ss'][index_merge],
                'faturamento': merge_localiza_autem['faturamento_loca'][index_merge],
                'ss_pre': merge_localiza_autem['ss_pre'][index_merge]
             }
             
             not_clear_ss.append(not_clear_ss_dict)
             
                   
    return clear_ss, not_clear_ss

##Google API
def download_attachments(gmail, ss: str, browser) -> str:
    
    #define the query to search for emails with a specific subject and attachments
    query = f'subject:"Localiza Gestão de Frotas 24 Horas - SS: {ss}" has:attachment'
    
    #search for query
    try:
        
        messages = gmail.get_messages(query=query)
    
    except Exception:
        
        print('Token do Gmail API expirado. Renicie o programa.')
        input('Enter para sair.')
        
        browser.quit()
        
        raise SystemExit
    
    #treat not finding messages
    if not messages:
        print("Nenhum e-mail encontrado")
        return 'error_e-mail_not_found'
    
    #locate and save the pdf to the proper location
    message = messages[0]
    attachment = message.attachments[0]
    # file_path = os.path.join("producao\jobs_csv\ss_pdf", attachment.filename)
    attachment.save(overwrite=True)
    default_path = attachment.filename
    custom_file_path = os.path.join("producao\jobs_csv\ss_pdf", attachment.filename)
    os.replace(default_path, custom_file_path)
    
    return attachment.filename
          
#extract the last four digits from the specific CNPJ   
def get_4_cnpj(filename) -> str:
    
    cnpj_pdf = fitz.open(f"producao\jobs_csv\ss_pdf\{filename}")
    
    for page_num, page in enumerate(cnpj_pdf):
        
        #extract all the text from the page
        text = page.get_text('text')
        
        #string to search for in all of the ss's pdfs
        search_string = 'S/A - CNPJ '
        
        #Find the single exact occurrence of the search string
        start_idx = text.find(search_string)
        
        if start_idx != -1:  # Found the search string
            
            #calculate the end index for the next 14 characters
            end_idx = start_idx + len(search_string) + 14
            snippet = text[start_idx + len(search_string):end_idx]

            #get only the last four characters of the 14-character snippet
            four_cnpj = snippet[-4:]
            
            break
        
    cnpj_pdf.close()
    return four_cnpj, snippet

jobs_localiza_autem()
