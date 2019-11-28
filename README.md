# scraping_news
Scraping livedoor web news.  
Collect 「keywords」「breadcrumbs」「summaries」「title」「article」.  

## 1. Collect category url
Collect category url and save as `category_url.txt`.  
Category url is like `http://news.livedoor.com/topics/category/sports/`.

## 2. Collect article url
Run `collect_article_url.py` for article url in category.

```shell
$ python collect_article_url.py
```

## 3. Collect articles
Run `scrape_articles.py`.  

```shell
$ python scrape_articles.py
```

Article data wil be saved as `articles.json`.
