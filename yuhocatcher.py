import neologdn
import re
import argparse
import os
import json
from tqdm import tqdm
from bs4 import BeautifulSoup
import time

def scrape(input_dir, output_dir):
    with open(input_dir, 'r') as rf, open(output_dir, 'w') as wf:
        df = json.load(rf)
    code = df["code"]

    basePath = "/Users/hotakahattori/zaisan-net/Disclosure_Information_Extraction/raw_data/"

    res = requests.get("https://resource.ufocatch.com/atom/edinetx/query/" + code)
    if res.status_code == 200:
        soup = BeautifulSoup(res.content, "xml")

        for element in soup.find_all("entry"):
            title = element.find("title").get_text()
            if re.search("有価証券報告書", title) != None:
                id = element.find("id").get_text()
                saveDirPath = basePath + id
                if not os.path.exists(saveDirPath):
                    os.mkdir(saveDirPath)
                pdf_url = re.sub("page", "/edinet",element.find("link").get("href"))
                xbrl_url = ""
                for child in element.find_all("link"):
                    if child.get("rel") == "related":
                        xbrl_url = child.get("href")
                        break
                print(pdf_url)
                print(xbrl_url)

                pdf = requests.get(pdf_url)
                pdf_filename = id + ".pdf"
                if not os.path.exists(saveDirPath + "/PDF"):
                    os.mkdir(saveDirPath + "/PDF")
                if pdf.status_code == 200:
                    with open(os.path.join(saveDirPath + "/PDF", pdf_filename),"wb") as f:
                        f.write(pdf.content)

                xbrl = requests.get(xbrl_url, stream = True)

                xbrl_filename = id
                if not os.path.exists(saveDirPath + "/XBRL"):
                    os.mkdir(saveDirPath + "/XBRL")
                if xbrl.status_code == 200:
                    xbrl_dirPath = saveDirPath + "/XBRL/" + id + ".zip"
                    with open(xbrl_dirPath,"wb") as f:
                        f.write(xbrl.content)
                    with zipfile.ZipFile(xbrl_dirPath) as existing_zip:
                        existing_zip.extractall(saveDirPath + "/XBRL")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-input', '--input_directory', dest='input', type=str, required=True)
    parser.add_argument('-ouput', '--output_directory', dest='output', type=str, required=True)
    args = parser.parse_args()

    input_directory = args.input
    output_directory = args.output
    input_directory = "/home/zaisan/sum/scraping_news/nikkei"
    output_directory = "/home/zaisan/sum/scraping_news/nikkei_pdf"
    if not os.path.exists(output_directory): os.makedirs(output_directory)
    sorted_input = sorted(os.listdir(input_directory))
    start = time.time()
    for f in sorted_input:
        input_path = os.path.join(input_directory, f)
        output_path = os.path.join(output_directory, f)
        scrape(input_path, output_path)
    elapsed_time = time.time()-start
    print(elapsed_time)

if __name__ == '__main__':
    main()