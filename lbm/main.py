import datetime
from multiprocessing import Pool
import os
import requests
from bs4 import BeautifulSoup
import csv
from defusedxml import minidom
import xml.etree.ElementTree as ET


def get_category():
    req = requests.get('https://drevodesign.ru/product/')
    soup = BeautifulSoup(req.text, 'lxml')
    all_category = soup.find(class_='item-views catalog sections').find_all('a')
    all_category = ['https://drevodesign.ru' + a.get('href') for a in all_category]
    all_category = set(all_category)
    return all_category



def get_data():
    category = get_category()
    print(category)
    dates = []
    cats = set()
    for cat in category:
        print(cat)
        req = requests.get(cat)
        soup = BeautifulSoup(req.text, 'lxml')
        if soup.find(class_='item-views catalog sections') != None:
            subcats = soup.find(class_='item-views catalog sections').find_all('a')
            subcats = [a.get('href') for a in subcats]
            for subcat in set(subcats):
                print(subcat)
                req = requests.get('https://drevodesign.ru' + subcat)
                soup = BeautifulSoup(req.text, 'lxml')
                catalog = soup.find(class_='section-content-wrapper')
                all_product = catalog.find_all(class_='item')
                for product in all_product:
                    if product != None:
                        data = []
                        name = product.find('span').text
                        sku = product.find(class_='article').text.split('\xa0')[1]
                        src = 'https://drevodesign.ru' + product.find('a').get('href')
                        img = 'https://drevodesign.ru' + product.find('img').get('src')
                        price = product.find(class_='price_val').text
                        req = requests.get(src)
                        soup = BeautifulSoup(req.text, 'lxml')
                        desc = soup.find(class_='content').text.replace('\r', '').replace('\n', '').strip()
                        is_avail = soup.find(class_='status-icon instock')
                        if is_avail == None:
                            is_avail = soup.find(class_='status-icon order')
                        is_avail = is_avail.text
                        if is_avail == 'В наличии':
                            is_avail = 'Да'
                        else:
                            is_avail = 'Нет'
                        ct = soup.find(class_='breadcrumb').find_all('li')
                        ct = [cat.text for cat in ct[2:-1]]
                        ct = '/'.join(ct).replace('\r', '').replace('\n', '')
                        data.append(ct)
                        data.append(name)
                        data.append(img)
                        data.append(sku)
                        data.append(src)
                        data.append(price)
                        data.append(desc)
                        data.append(is_avail)
                        cats.add(ct)
                        dates.append(data)
        else:
            catalog = soup.find(class_='section-content-wrapper')
            all_product = catalog.find_all(class_='item')
            for product in all_product:
                if product != None:
                    data = []
                    name = product.find('span').text
                    sku = product.find(class_='article').text.split('\xa0')[1]
                    src = 'https://drevodesign.ru' + product.find('a').get('href')
                    img = 'https://drevodesign.ru' + product.find('img').get('src')
                    price = product.find(class_='price_val').text
                    req = requests.get(src)
                    soup = BeautifulSoup(req.text, 'lxml')
                    desc = soup.find(class_='content').text.replace('\r', '').replace('\n', '').strip()
                    ct = soup.find(class_='breadcrumb').find_all('li')
                    ct = [cat.text for cat in ct[2:-1]]
                    ct = '/'.join(ct).replace('\r', '').replace('\n', '')
                    is_avail = soup.find(class_='status-icon instock')
                    if is_avail == None:
                        is_avail = soup.find(class_='status-icon order')
                    is_avail = is_avail.text
                    if is_avail == 'В наличии':
                        is_avail = 'Да'
                    else:
                        is_avail = 'Нет'
                    data.append(ct)
                    data.append(name)
                    data.append(img)
                    data.append(sku)
                    data.append(src)
                    data.append(price)
                    data.append(desc)
                    data.append(is_avail)
                    cats.add(ct)
                    dates.append(data)
    with open(f'fidstore/drevodesign/drevodesign.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for data in dates:
            writer.writerow(data)
    return dates, cats


def make_xml_drevodesign():
    yml_catalog = ET.Element('yml_catalog')
    yml_catalog.set('date',
                    f'{datetime.date.today()} {datetime.datetime.today().hour}:{datetime.datetime.today().minute}')
    shop = ET.SubElement(yml_catalog, 'shop')
    name_shop = ET.SubElement(shop, 'name')
    company_shop = ET.SubElement(shop, 'company')
    url_shop = ET.SubElement(shop, 'url')

    name_shop.text = 'drevodesign'
    company_shop.text = 'drevodesign.ru'
    url_shop.text = 'https://drevodesign.ru/'

    currencies = ET.SubElement(shop, 'currencies')
    currency = ET.SubElement(currencies, 'currency')
    currency.set('id', 'RUB')
    currency.set('rate', '1')
    set_cat = set()
    dates = []
    with open('fidstore/drevodesign/drevodesign.csv', 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            set_cat.add(row[0])
            dates.append(row)
    cats = {}
    j = 1
    for i in set_cat:
        print(i.replace('\r', '').replace('\n', ''))
        cats[i.replace('\r', '').replace('\n', '')] = str(j)
        j += 1
    categories = ET.SubElement(shop, 'categories')
    for i in cats:
        category = ET.SubElement(categories, 'category')
        category.set('id', cats[i])
        category.text = i
    offers = ET.SubElement(shop, 'offers')
    products = []
    for data in dates:
        product = {
            "Категория": 'cats[data[0].replace('\r', '').replace('\n', '')]',
            "Фото": data[2].replace('\r', '').replace('\n', ''),
            "Ссылка": data[4].replace('\r', '').replace('\n', ''),
            "Название": data[1].replace('\r', '').replace('\n', ''),
            "Цена": data[5].replace('\r', '').replace('\n', '').strip().replace(' ','').replace('От',''),
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
            price.text = product['Цена'][:-4]
        currencyId = ET.SubElement(offer, 'currencyId')
        currencyId.text = 'RUB'
        url = ET.SubElement(offer, 'url')
        url.text = product['Ссылка']
        description = ET.SubElement(offer, 'description')
        description.text = product['Описание']
    xml_string = ET.tostring(yml_catalog).decode()
    xml_prettyxml = minidom.parseString(xml_string).toprettyxml()
    with open("fidstore/drevodesign/drevodesign.xml", 'w', encoding="utf-8") as xml_file:
        xml_file.write(xml_prettyxml)
    tree = ET.parse("fidstore/drevodesign/drevodesign.xml")
    root = tree.getroot()
    tree.write("fidstore/drevodesign/drevodesign.xml", encoding='utf-8', xml_declaration=True)

def start_parse_drevodesign():
    # get_data()
    make_xml_drevodesign()

headers = {
    'accept': '*/*',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0',
    'Upgrade-Insecure-Requests': '1',
}
req = requests.get('https://lbmgroup.ru/hits', headers=headers,)
print(req.status_code)
with open('test.html','w', encoding='utf-8') as file:
    file.write(req.text)
