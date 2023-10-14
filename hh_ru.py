import requests
import json
import re

from bs4 import BeautifulSoup
from fake_headers import Headers


url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
header = Headers(headers=True).generate()

resp = requests.get(url, headers=header)
soup = BeautifulSoup(resp.text, 'lxml')

vacancy_list = soup.find_all('div', {'class': 'serp-item'})[2:]
vacancy_result = []

for item in vacancy_list:
    item_url = item.find('a', class_='serp-item__title').get('href').split('?')[0]
    item_resp = requests.get(item_url, headers=header)
    item_soup = BeautifulSoup(item_resp.text, 'lxml')
    description = item_soup.find('div', {'data-qa': 'vacancy-description'}).text
    if ('django' and 'flask') in description.lower():
        vacancy_dict = {}
        vacancy_dict['url'] = item_url
        salary = item_soup.find('span', {'data-qa': 'vacancy-salary-compensation-type-net'})
        vacancy_dict['salary'] = re.sub(r'\xa0', '', salary.text) if salary else 'размер ЗП не указан'
        vacancy_dict['name'] = re.sub(r'\xa0',' ', item_soup.find('span', class_='vacancy-company-name').text)
        address_company1 = item_soup.find('p', {'data-qa': 'vacancy-view-location'})
        address_company2 = item_soup.find('div', {'data-qa': 'vacancy-serp__vacancy-address'})
        vacancy_dict['address'] = (address_company2 if address_company2 else address_company1).text
        vacancy_result.append(vacancy_dict)

with open('vacancy.json', 'w') as json_file:
    json.dump(vacancy_result, json_file, indent=4, ensure_ascii=False)