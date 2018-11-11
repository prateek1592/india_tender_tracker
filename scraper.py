import pandas as pd
from bs4 import BeautifulSoup
import requests

base_url = 'https://eprocure.gov.in/cppp/searchbyorg/'
base_url += 'Ministry%20of%20Road%20Transport%20and%20Highways/page='

def get_all_urls(base_url):    
    text = requests.get(base_url + str(1)).text
    soup = BeautifulSoup(text, 'lxml')    
    page_num_range = []
    num_pages_obj = soup.find_all(attrs = {"class": "page_parination"})
    
    for obj in num_pages_obj:
        try:
            page_num_range.append(int(obj.text))
        except:
            pass
        
    page_num_range = sorted(list(set(page_num_range)))
    urls = [base_url + str(x) for x in page_num_range]
    return urls


def get_table(urls):    
    data = []    
    for url in urls:    
        text = requests.get(url).text
        soup = BeautifulSoup(text, 'lxml')            
        table_body = soup.find("table", attrs = {"class": "list_table"})    
        rows = table_body.find_all('tr')
        for i, row in enumerate(rows):
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            if i == 0:
                header = cols
            else:
                data.append([ele for ele in cols if ele])
    
    data = pd.DataFrame(data, columns = header)
    cols_2_extract = ['e-Published Date', 'Bid Submission Closing Date', 'Tender Opening Date']
    data[cols_2_extract] = data[cols_2_extract].applymap(lambda x : pd.to_datetime(x[:11], format = '%d-%b-%Y'))
    data = data.sort_values('e-Published Date', ascending = False)
    return data


list_of_urls = get_all_urls(base_url)
tender_information = get_table(list_of_urls)
tender_information.to_csv('output.csv', index=False)