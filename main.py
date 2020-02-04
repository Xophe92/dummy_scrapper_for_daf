# coding: utf-8

from bs4 import BeautifulSoup
import urllib3
import xlsxwriter
import re
import requests
import sys

py_version = sys.version_info[0]

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


url_radicals = "https://m.materielelectrique.com/bisou-daffounet-p-{}.html"

urls = [url_radicals.format(str(i)) for i in range(1, 5)]


def make_soup(url):
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    return BeautifulSoup(r.data,'lxml')

information_to_find = [
{"tag_type" : "h1", "attribute_name":"itemprop", "attribute_value":"name", "data_in":"text"},
{"tag_type" : "meta", "attribute_name":"itemprop", "attribute_value":"gtin13", "data_in":"content"},
{"tag_type" : "meta", "attribute_name":"itemprop", "attribute_value":"priceCurrency", "data_in":"content"},
{"tag_type" : "span", "attribute_name":"itemprop", "attribute_value":"price", "data_in":"content"},
{"tag_type" : "div", "attribute_name":"itemprop", "attribute_value":"description", "data_in":"html"},
{"tag_type" : "img", "attribute_name":"itemprop", "attribute_value":"image", "data_in":"src"},
{"tag_type" : "div", "attribute_name":"class", "attribute_value":"section small grey", "data_in":"reg_exp", "reg_exp":u"Référence : (.+)"},
]


def download_file(url, filename):

    with open(filename, 'wb') as handle:
            response = requests.get(url, stream=True)

            if not response.ok:
                print (response)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)

headlines = [info["attribute_value"] for info in information_to_find]
row = 0

workbook = xlsxwriter.Workbook('catalog.xlsx')
worksheet = workbook.add_worksheet()

for col, title in enumerate(headlines):
    worksheet.write(row, col+1, title)

for url in urls:
    print(url)
    row +=1
    worksheet.write(row, 0 , url)

    try:
        soup = make_soup(url)

        for col, info in enumerate(information_to_find):
            result = soup.find_all(info["tag_type"], {info["attribute_name"] : info["attribute_value"]})[0]

            if info["data_in"] == "text":
                content_to_save = result.get_text()
            elif info["data_in"] == "html":
                content_to_save = str(result)
            elif info["data_in"] == "reg_exp":
                content_to_save = re.search(info["reg_exp"], result.get_text()).group(1)
                reference = content_to_save
            else:
                content_to_save = result[info["data_in"]]

            if info["attribute_value"] == "image":
                image_url = content_to_save.replace("_preview", "_large")
            if py_version == 3:
                worksheet.write(row, col+1 , content_to_save)
            else:
                worksheet.write(row, col+1 , content_to_save.decode("utf-8"))
        download_file(image_url, reference+".jpeg")
    except Exception as e:        
        print(e)
        print("foirage sur {}".format(url))

workbook.close()

