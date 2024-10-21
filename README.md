# reboque_script
Automated routine for manual labourous tasks executed within a service in a towing company.

The task objective is to generate digital invoices to services rendered with the company. More specifically, the company in question, Reboque, works with another company, Localiza, to which the services are offered.

There are four external services used for the task. E-mail provider (Google), Localiza, Autem and Nota Carioca. All of those are utilized in the same system, Google Chrome, and require credentials to initiate the task. The login will be executed by Selenium before the steps begin.

Briefly, Localiza website expects the invoices from Nota Carioca to be uploaded to each job listed.

In depth, the steps to the whole routine are as follows:

#1 – Identify jobs that are not to be ran through the script.

There are some jobs listed that do not apply, either because the job generated no value, or the value does not match the control.

This step is to be done by scraping Localiza job dashboard into a dictionary or dataset and compare each pair of monetary value and job identifier with the analogous in the control dataset, accessed in a service called autem.com, that will also be transformed into a workable and comparable dataset.

If the job is marked positive in this step, it will be skipped and analyzed manually.

The rule will be: if the value is lower, it will be marked positive. If the value is equal or greater, it will be marked negative. Another rule is, within autem's dashboard the column "&nbsp\;" must be observed. If it is red, do not proceed.

#2 – Extract the specific Localiza company ID (CNPJ) from an e-mail PDF attachment.

Besides the Localiza data table, each job is also consolidated with an e-mail that contains information about the job, including price and identification.

Localiza is made up of many different company IDs, based on location. The job will carry the specific company ID based on where it physically happened. The control website, autem.com, does not have this information, thus, it had to be inputted manually. 

Upon locating the e-mail and extracting the CPNJ number within the standard PDF layout, it will be stored for later and autem.com will be updated automatically, using Selenium, with the last 4 numbers on the CNPJ identifier, as it requires.

#3 – Update the current job on Localiza dashboard with pertinent information.

Each job needs to be filled with standard and changing data on it’s own panel within the Localiza dashboard, such as Reboque company CNPJ and other job specific data. Other data include, date, job value and others. Static data will be stored beforehand and changing information will be scraped.

#4 – Download the invoice from Nota Carioca website and upload it to Localiza.

The last field to be filled within the current job’s panel is the invoice itself. It will be acquired on Nota Carioca website. 

After logging in, the job’s location specific CNPJ that was extracted from the e-mail’s PDF will be inputted, and the site will offer the invoice, including a download option, after which, the file location will be stored and fed to Localiza.

-

This will be the main cycle. Logs will be generated with every relevant step, for control and debugging. Initially, the user will have to inform how many jobs will be checked and ran through a JSON, or other text file. There will be no GUI, for the moment.
