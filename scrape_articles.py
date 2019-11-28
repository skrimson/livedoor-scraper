import os
import requests
from bs4 import BeautifulSoup
from joblib import Parallel, delayed
from retrying import retry
import time
import json
import sys
import tqdm

output_directory = "./livedoor"


def main():
    with open("article_url.txt") as f:
        url_list = list(set([line.strip() for line in f]))
    if not os.path.isdir(output_directory):
        os.makedirs(output_directory)

    # 既に検索済みの記事かどうかのチェック
    # with open("articles.json", encoding="utf-8") as f:
    #     url_json = json.load(f)
    # downloaded_url = set([d["url"] for d in url_json["data"]])
    # url_list = [url for url in url_list if url not in downloaded_url]

    url_list = [url for url in url_list]

    result = Parallel(n_jobs=-1)([delayed(collect_data)(url) for url in url_list])
    removed = [res for res in result if res]
    print(len(removed))


def collect_data(url):
    try:
        summaries, _ = get_summary(url)
        url_id = url[-9:-1]
        if summaries:
            article, _, title, = get_article_data(url.replace("topics", "article"))
            if article and len(article) >= 300:
                dic = {
                    "id" : url_id,
                    "title": title,
                    "url": url,
                    "summaries": summaries,
                    "article": article
                }
                write(dic)
                return dic
            else:
                return {}
        else:
            return {}
    except Exception as e:
        print(e)
        return {}


def retry_if_status_code_not_200(tup):
    return tup[1] != 200

@retry(retry_on_result=retry_if_status_code_not_200, stop_max_attempt_number=10)
def get_summary(url):
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        # topicsページにリクエストが成功
        time.sleep(2)
        bs = BeautifulSoup(res.text, "html.parser")
        summary_body = bs.find(class_="summaryBody")
        if summary_body is not None:
            summaries = [li.get_text() for li in summary_body.find_all("li")]
            return (summaries, res.status_code)
        else:
            return ([], res.status_code)
    else:
        # リクエストが失敗
        time.sleep(2)
        return ("", res.status_code)


@retry(retry_on_result=retry_if_status_code_not_200, stop_max_attempt_number=10)
def get_article_data(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"}
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        # topicsページにリクエストが成功
        time.sleep(2)
        bs = BeautifulSoup(res.text, "html.parser")
        article_body = bs.find(class_="articleBody")
        if not article_body:
            # ページ内になんらかの理由で記事がなかった
            return ("", res.status_code, "")

        title = bs.find(class_="articleTtl").get_text() if bs.find(class_="articleTtl") else bs.find(class_="topicsTtl").get_text()
        texts = article_body.find("span").find_all("p")
        # 記事本文のフォーマットに合わせて条件分岐
        if texts:
            article = "".join([p.get_text().replace("¥u3000", "") for p in texts])
            return (article, res.status_code, title)
        else:
            article = article_body.find("span")
            if article.find("script"):
                article.find("script").extract()
            article = article.get_text()
            return (article.strip().replace("¥u3000", ""), res.status_code, title)
    else:
        # リクエストが失敗
        time.sleep(2)
        return ("", res.status_code)

def write(dic):
    with open(os.path.join(output_directory, dic["id"]), "w") as f:
        f.write(dic["article"] + "\n@highlight\n" + "。".join(dic["summaries"])) 


if __name__ == "__main__":
    main()
