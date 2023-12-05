from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import datetime
from multiprocessing import Pool
import os
import requests
from bs4 import BeautifulSoup
import csv
import time
from defusedxml import minidom
import xml.etree.ElementTree as ET
driver = webdriver.Firefox(executable_path='geckodriver.exe')
driver.get("https://lbmgroup.ru/hits")
time.sleep(4)
soup = BeautifulSoup(driver.page_source, 'lxml')
products = soup.find_all(class_='t-cover')
data = []
for product in products:
    ct = 'Строительство'
    name = product.find(class_='t922__title t-name t-name_xl js-product-name').text
    sku = product.find(class_='t922__title_small t-descr t-descr_xxs').text
    price = product.find(class_='t922__price-value js-product-price notranslate').text
    desc = product.find(class_='t922__descr t-descr t-descr_xxs').text
    img = product.find(class_='js-product-img').get('data-content-cover-bg')
    is_avail = 'Да'
    src = product.find(class_='t922__btn t-btn t-btn_sm').get('href')
    data.append([ct,name,img,sku,src,price,desc,is_avail])
    print(data)
driver.close()
with open(f'lbm.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in data:
            writer.writerow(row)



def make_xml_lbm():
    yml_catalog = ET.Element('yml_catalog')
    if len(str(datetime.datetime.today().minute)) == 1:
        yml_catalog.set('date',
                    f'{datetime.date.today()} {datetime.datetime.today().hour}:0{datetime.datetime.today().minute}')
    else:
        yml_catalog.set('date',
                    f'{datetime.date.today()} {datetime.datetime.today().hour}:{datetime.datetime.today().minute}')
    shop = ET.SubElement(yml_catalog, 'shop')
    name_shop = ET.SubElement(shop, 'name')
    company_shop = ET.SubElement(shop, 'company')
    url_shop = ET.SubElement(shop, 'url')

    name_shop.text = 'lbm'
    company_shop.text = 'lbm.ru'
    url_shop.text = 'https://lbmgroup.ru/'

    currencies = ET.SubElement(shop, 'currencies')
    currency = ET.SubElement(currencies, 'currency')
    currency.set('id', 'RUB')
    currency.set('rate', '1')
    set_cat = set()
    dates = []
    with open('lbm.csv', 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            dates.append(row)
    categories = ET.SubElement(shop, 'categories')
    category = ET.SubElement(categories, 'category')
    category.set('id', "1")
    category.text = 'Строительство'
    offers = ET.SubElement(shop, 'offers')
    products = []
    for data in dates:
        product = {
            "Категория": '1',
            "Фото": data[2].replace('\r', '').replace('\n', ''),
            "Ссылка": data[4].replace('\r', '').replace('\n', ''),
            "Название": data[1].replace('\r', '').replace('\n', ''),
            "Цена": data[5].replace('\r', '').replace('\n', '').strip().replace(' ','').replace('от',''),
            "Артикул": data[3].replace('\r', '').replace('\n', ''),
            "В наличии": data[7].replace('\r', '').replace('\n', ''),
            "Описание": data[6].replace('\r', '').replace('\n', ''),
        }
        offer = ET.SubElement(offers, 'offer')
        offer.set('id', str(product['Артикул']))
        offer.set('available', 'true')
        products.append(product)
        name = ET.SubElement(offer, 'name')
        name.text = product['Название']
        categoryId = ET.SubElement(offer, 'categoryId')
        categoryId.text = product['Категория']
        picture = ET.SubElement(offer, 'picture')
        picture.text = product['Фото']
        if product['Цена'] != 'Позапросу':
            price = ET.SubElement(offer, 'price')
            price.text = product['Цена']
        currencyId = ET.SubElement(offer, 'currencyId')
        currencyId.text = 'RUB'
        url = ET.SubElement(offer, 'url')
        url.text = product['Ссылка']
        description = ET.SubElement(offer, 'description')
        description.text = product['Описание']
    xml_string = ET.tostring(yml_catalog).decode()
    xml_prettyxml = minidom.parseString(xml_string).toprettyxml()
    with open("lbm.xml", 'w', encoding="utf-8") as xml_file:
        xml_file.write(xml_prettyxml)
    tree = ET.parse("lbm.xml")
    root = tree.getroot()
    tree.write("lbm.xml", encoding='utf-8', xml_declaration=True)

make_xml_lbm()