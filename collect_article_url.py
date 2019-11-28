from bs4 import BeautifulSoup
import requests
from joblib import Parallel, delayed
from retrying import retry
import time


def main():
    with open("category_url.txt") as f:
        category_urls = [line for line in f]

    ua_chrome = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36"
    final_url_list = []
    for url in category_urls:
        result = Parallel(n_jobs=-1)( [delayed(get_content_page)(url, page_num+1, ua_chrome) for page_num in range(300)])
        for r in result:
            final_url_list.extend(r[0])

    with open("article_url.txt", "w") as f:
        for url in final_url_list:
            f.write(url + "\n")


def retry_if_status_code_not_200(tup):
    return tup[1] != 200


@retry(retry_on_result=retry_if_status_code_not_200)
def get_content_page(url, page_num, user_agent):
    payload = {"p": page_num}
    headers = {"User-Agent": user_agent}
    res = requests.get(url, params=payload, headers=headers)
    if res.status_code == 200:
        time.sleep(2)
        bs = BeautifulSoup(res.text, "html.parser")
        article_list = bs.find(class_="articleList")
        urls = [li.find("a").get("href") for li in article_list.find_all("li")]
        return (urls, res.status_code)
    else:
        time.sleep(2)
        return ("", res.status_code)


if __name__ == "__main__":
    main()
