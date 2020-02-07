from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import numpy as np
import pandas as pd
import re
import time
import csv
import os
import json

def get_urls():
    options = Options()
    options.set_headless()
    #Chromeを操作
    driver = webdriver.Chrome(options=options)

    # Gyoseki news
    target_url='https://www.nikkei.com/markets/kigyo/index/?bn=1&uah=DF_SEC8_C2_060'
    driver.get(target_url)

    # CSV file output
    urls = []

    while 1 :
        time.sleep(5)
        html = driver.page_source

        # BeautifulSoup 
        soup = BeautifulSoup(html, 'html.parser')
        sel = soup.find_all("h4",attrs={"class":"m-article_title"})

        for i in range(0, len(sel)):
            if sel[i].find('span', class_='m-iconMember') == None :
                urls.append(sel[i].a.get("href"))

        # Next Page
        try :
            driver.find_element_by_link_text('次へ').click()
        except Exception as e:
            print(e)
            break

    driver.quit()

    resdata = np.vstack([urls])
    df = pd.DataFrame(data=resdata).T
    df.to_csv('result.csv', header=False, index=False)

def scrape():
    output_dir = "/home/zaisan/sum/scraping_news/nikkei"
    options = Options()
    options.set_headless()
    #Chromeを操作
    driver = webdriver.Chrome(options=options)
    with open("result.csv", "r") as urls:
        for url in urls:
            dic = {}
            url = url.strip("\n")
            driver.get("https://www.nikkei.com" + url)
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            title = soup.find("span",attrs={"class":"cmnc-middle JSID_key_fonthln m-streamer_medium"}).string
            body = soup.find("div",attrs={"class":"cmn-article_text a-cf JSID_key_fonttxt m-streamer_medium"})
            body_list = []
            for b in body.findAll('p'):
                body_list.append(b.text)
            body = "".join(body_list)
            dic["article"] = body.split("。")
            dic["abstract"] = title.split("。")
            json_file = open(output_dir+"{}.json".format(url[8:-1]), "w")
            json.dump(dic, json_file, indent=4, ensure_ascii=False)
            
if __name__ == "__main__":
    get_urls()
    scrape()