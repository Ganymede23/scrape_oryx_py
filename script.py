import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from datetime import date, datetime, timedelta
import time
from urls import URLs

pd.set_option('display.max_rows', None)
print('Running...')

for item in URLs:
    url, actual_date = item
    time_counter_start = datetime.now()
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="post-body-8087922975012177708")

    if url != "https://www.oryxspioenkop.com/2022/02/attack-on-europe-documenting-equipment.html":
        source_date = datetime(year=int(url[28:32]), month=int(url[32:34]), day=int(url[34:36]))
        if not actual_date: # Assigns previous date in case the next day URL was used
            source_date -= timedelta(days=1)
    else:
        source_date = datetime.utcnow()
 
    # TYPES

    all_h3 = results.find_all('h3')

    equipment_types_auto_tmp = []
    equipment_types_auto = []

    # Gets all the types of equipment
    for h3 in all_h3:
        if not 'Ukraine' in h3.get_text() and not 'Russia' in h3.get_text():
            equipment_type = h3.get_text().partition("(")[0]
            equipment_type = re.sub(r"\s$", "", equipment_type)
            equipment_types_auto_tmp.append([equipment_type])

    # Gets rid of repeated elements
    for i in equipment_types_auto_tmp:
        if i not in equipment_types_auto:
            equipment_types_auto.append(i)

    # Turns 'lists of lists of strings' into just a list of strings
    equipment_types_auto = [val for sublist in equipment_types_auto for val in sublist]
    equipment_types_auto.remove('')

    equipment_types_auto

    # SUBTYPES

    equipment_subtypes_auto_tmp = []
    equipment_subtypes_auto = []

    all_li = results.find_all('li', attrs={'class': None})

    # Gets all the subtypes of equipment
    for li in all_li:
        equipment_subtype = re.search(r'(.*):', li.get_text())
        if equipment_subtype is not None:
            equipment_subtype = equipment_subtype.group(0)
            equipment_subtype = re.sub("^ \d+", "", equipment_subtype)
            equipment_subtype = re.sub(":", "", equipment_subtype)
            equipment_subtype = re.sub(r"^\s", "", equipment_subtype)
            equipment_subtypes_auto_tmp.append([equipment_subtype])

    # Gets rid of repeated elements
    for i in equipment_subtypes_auto_tmp:
        if i[0] not in equipment_subtypes_auto:
            equipment_subtypes_auto.append(i[0])

    equipment_subtypes_auto

    # STATUS

    status_types_auto_tmp = []
    status_types_auto = []

    all_a = results.find_all('a')

    # Gets all the statuses of equipment
    for a in all_a:
        status = re.search(r"\((.*)\)", a.get_text())
        if status is not None: 
            status = status.group(0)
            status = re.sub("\(", "", status)
            status = re.sub("\)", "", status)
            status = re.search(r"([^\,]+$)", status)
            status = status.group(0)        
            status = re.sub(r"^\s", "", status)
            status_types_auto_tmp.append([status])

    # Gets rid of repeated elements
    for i in status_types_auto_tmp:
        if i[0] not in status_types_auto:
            status_types_auto.append(i[0])

    status_types_auto

    for h3_i in all_h3:
        if h3_i.get_text().count('Ukraine') == 1:
            all_russian = h3_i.find_all_previous(['h3','ul'])
            all_ukraine = h3_i.find_all_next(['h3','ul'])

    all_russian_all_ukraine = [all_russian, all_ukraine]

    list_tmp = []

    country = 'RUS'

    for section in all_russian_all_ukraine:

        if all_russian_all_ukraine.index(section) == 1:
            country = 'UKR'
            
        for element in section:

            if element.name == 'h3':
                
                for equipment_type_i in equipment_types_auto:
                    
                    equipment_type = element.get_text().partition("(")[0]
                    equipment_type = re.sub(r"\s$", "", equipment_type)
                    
                    if equipment_type_i == equipment_type:
                        current_type = equipment_type_i
                    
                ul = element.nextSibling.nextSibling
                
                try:
                    
                    li_list = ul.find_all('li')
                    
                    for li in li_list:
                        
                        strEmpty = str(element)
                        
                        if current_type == 'Surface-To-Air Missile Systems' and country == 'UKR':
                            
                            strEmpty_find = re.search(r"<h3>[\r\n]</h3>", strEmpty)
                            
                            if not strEmpty_find == None:
                                break
                            

                        li_a_list = li.find_all('a')

                        for equipment_subtype_i in equipment_subtypes_auto:

                            equipment_subtype = re.search(r'(.*):', li.get_text())

                            if equipment_subtype is not None:

                                equipment_subtype = equipment_subtype.group(0)
                                equipment_subtype = re.sub("^ \d+", "", equipment_subtype)
                                equipment_subtype = re.sub(":", "", equipment_subtype)
                                equipment_subtype = re.sub(r"^\s", "", equipment_subtype)

                                if equipment_subtype_i == equipment_subtype:
                                    current_subtype = equipment_subtype_i

                        for status_i in status_types_auto:

                            for single_report in li_a_list:

                                current_a_text = single_report.get_text()

                                report_numbers = re.search(r"((?:\d+,\s*)+\d+\sand\s\d+|\d+,|\d+\sand\s\d+)", current_a_text)

                                try:
                                    report_numbers_string = report_numbers.group()
                                    report_numbers_string = re.sub("and", "", report_numbers_string)
                                    report_numbers_string = re.sub(",", "", report_numbers_string)
                                    report_numbers_count = len(report_numbers_string.split())
                                except:
                                    pass

                                current_a_text = re.sub("\(", "", current_a_text)
                                current_a_text = re.sub("\)", "", current_a_text)  
                                current_a_text = re.search(r"([^\,]+$)", current_a_text)

                                try:
                                    current_a_text = current_a_text.group(0)
                                    current_a_text = re.sub(r"^\s", "", current_a_text)
                                    if status_i == current_a_text:
                                        for x in range(0, report_numbers_count):
                                            if "https://web.archive.org/web/" in single_report['href']: #If the link is from Web Archive, deletes the first part of it.
                                                list_tmp.append([country, current_type, current_subtype, current_a_text, single_report['href'][43:].strip(), source_date.strftime("%d-%m-%Y")])
                                                #[43:] removes the web.archive.org part from the links
                                            else:
                                                list_tmp.append([country, current_type, current_subtype, current_a_text, single_report['href'].strip(), source_date.strftime("%d-%m-%Y")])
                                except Exception as e:
                                    #print(e)
                                    pass
                    
                except Exception as e: 
                    #print(e)
                    pass

    #Console log purposes
    time_counter = (datetime.now() - time_counter_start).total_seconds()
    dt_string = source_date.strftime("%B %d, %Y")
    print(' -', dt_string, 'scraped in', round(time_counter,2), 'seconds')

    #Export
    df = pd.DataFrame(list_tmp, columns=['country', 'equipment_type', 'equipment_subtype', 'status', 'source', 'date'])

    df

    cwd = os.getcwd()
    dt_string = source_date.strftime("%Y-%m-%d")
    path = cwd + '\output_files' + '/' + dt_string + '.csv'
    df.to_csv(path)

elapsed_time = time.perf_counter()
print(' - Total elapsed time:', round(elapsed_time,2), 'seconds')