from bs4 import BeautifulSoup
import urllib3
import xlsxwriter

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


url_radicals = "https://m.materielelectrique.com/bisou-daffounet-p-{}.html"

urls = [url_radicals.format(str(i)) for i in range(103091, 103095)]
print(urls)


def make_soup(url):
    http = urllib3.PoolManager()
    r = http.request("GET", url)
    return BeautifulSoup(r.data,'lxml')

information_to_find = [
{"tag_type" : "h1", "itemprop":"name", "data_in":"text"},
{"tag_type" : "meta", "itemprop":"gtin13", "data_in":"content"},
{"tag_type" : "meta", "itemprop":"priceCurrency", "data_in":"content"},
{"tag_type" : "span", "itemprop":"price", "data_in":"content"},
{"tag_type" : "div", "itemprop":"description", "data_in":"text"},
{"tag_type" : "img", "itemprop":"image", "data_in":"src"},
]


headlines = [info["itemprop"] for info in information_to_find]
row = 0

workbook = xlsxwriter.Workbook('catalog.xlsx')
worksheet = workbook.add_worksheet()

for col, title in enumerate(headlines):
    worksheet.write(row, col, title)

for url in urls:
    row +=1
    worksheet.write(row, col , url)

    try:
        soup = make_soup(url)

        for col, info in enumerate(information_to_find):
            result = soup.find_all(info["tag_type"], {"itemprop" : info["itemprop"]})[0]
            if info["data_in"] == "text":
                worksheet.write(row, col , result.get_text())
            else:    
                worksheet.write(row, col , result[info["data_in"]])
    except:
        print("foirage sur {}".format(url))
workbook.close()

