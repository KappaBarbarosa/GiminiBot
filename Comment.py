import requests
from bs4 import BeautifulSoup
import re
import json

import google.generativeai as genai
genai.configure(api_key='AIzaSyAY6Q1GIxBg-s5ocjPxwvjh1D0IB-nKglY')
Textmodel = genai.GenerativeModel('gemini-1.5-flash')
print("Textmodel loaded.")

def search_momo(keyword):
  def extract_goods_code(url):
    # 使用正則表達式來匹配商品代碼
    match = re.search(r'i_code=(\d+)', url)
    if match:
        return match.group(1)
    else:
        return None
  def parse_search_results(html):
    soup = BeautifulSoup(html, 'html.parser')
    product_name_and_id = []

    # 查找所有商品連結，位於 <li class="goodsItemLi goodsItemLiSeo"> 中
    for item in soup.find_all('li', class_='goodsItemLi goodsItemLiSeo'):
      link_tag = item.find('a')
      if link_tag:
        link = link_tag['href']
        title = link_tag['title']
        product_name_and_id.append((title, extract_goods_code(link)))

    return product_name_and_id
  # 構建搜索 URL
  base_url = "https://m.momoshop.com.tw/search.momo"
  headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
      "Accept-Encoding": "gzip, deflate, br",
      "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7"
  }
  params = {
      "searchKeyword": keyword,
      "_isFuzzy": "0",
      "searchType": "1"
  }
  response = requests.get(base_url, params=params, headers=headers, timeout=20)

  if response.status_code == 200:
    res = parse_search_results(response.text)
    if res:
      return res
    else:
      print("No search results found.")
      return None
  else:
      print(f"Failed to retrieve search results. Status code: {response.status_code}")
      return None

def get_reviews_momo(goods_code, page=1, filter_type="total", multi_filter_type=["hasComment"], cust_no=""):
  """
  使用momo API取得商品評論(AJAX)

  TODO:
  1. handle 可能會有不只一個頁面，AJAX回傳的是第一個頁面的結果
  2. 如果正則表達失效，或是其他部分失效該怎麼辦。
  """


  url = "https://eccapi.momoshop.com.tw/user/getGoodsCommentList"
  # 提取商品代碼
  headers = {
    "Content-Type": "application/json",
    "version": "5.31.0"
  }
  payload = {
    "host": "mobile",
    "goodsCode": goods_code,
    "curPage": page,
    "filterType": filter_type,
    "custNo": cust_no,
    "multiFilterType": multi_filter_type
  }
  response = requests.post(url, json=payload, headers=headers)
  try:
    if response.status_code == 200:
      # print(response.json())
      return [i['comment'] for i in response.json()['goodsCommentList']]
    else:
      print(f"Failed to retrieve comment list. Status code: {response.status_code}")
      return []
  except: # 有可能沒有評論，或著沒有有字的評論
    return []

def search_shopee(keyword):
  pass
def search_amazon(keyword='A53', log=False):
  '''
    Note: amazon 反爬蟲很強，可能要定期更換標頭
  '''
  search_url = f"https://www.amazon.com/s?k={keyword}&crid=2T1N8D1ONMEVO&sprefix=%2Caps%2C269&ref=nb_sb_ss_recent_2_0_recent"
  headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja-JP;q=0.6,ja;q=0.5",
    "Cache-Control": "max-age=0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Cookie": "session-id=134-1997723-2740352; i18n-prefs=USD; sp-cdn=\"L5Z9:TW\"; ubid-main=134-2385468-8031165;",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Referer": "https://www.amazon.com/"
  }
  res = []
  response = requests.get(search_url, headers=headers)
  if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    products = soup.find_all('h2')
    for product in products[1:]:
      try:
        name = product.find('a').get_text()
        href = product.find('a')['href']
        res.append((name, "https://www.amazon.com"+href))
      except:
        # 可能有一些h2是雜訊，e.g. "結果" "更多結果"
        if log: print(product)
      if log: print(name + ": " + "https://www.amazon.com"+href)
  else:
    print(f"Failed to retrieve Amazon data. Status code: {response.status_code}")
  return res

def get_reviews_amazon(link, log=False):
  # amazon 找不到商品ID(反正我沒找到)，所以先以link方式爬蟲
  headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7,ja-JP;q=0.6,ja;q=0.5",
    "Cache-Control": "max-age=0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Cookie": "session-id=134-1997723-2740352; i18n-prefs=USD; sp-cdn=\"L5Z9:TW\"; ubid-main=134-2385468-8031165;",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Referer": "https://www.amazon.com/"
  }
  reviews = []
  response = requests.get(link, headers=headers)
  if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    # 找到所有評論的連結
    reviews_span = soup.find_all('span', class_='cr-original-review-content')
    for rev in reviews_span:
      try:
        reviews.append(rev.get_text())
      except:
        pass
      if log: print(rev.get_text())
  else:
    print(f"Failed to retrieve Amazon data. Status code: {response.status_code}")
  return reviews

def filter_result_by_llm(product_name_and_id):
  """
  使用 LLM 進行篩選，將不相關的商品連結移除。
  """
  # TODO
  return product_name_and_id

def CommentAPI(query="iphone15",Textmodel=None, website='amazon', limit=20,k=80, log=False):
  '''
    keyword: 關鍵字
    website: 搜尋網站
    limit: 取得幾筆結果
    log: 是否印出過程與結果
  '''
  
  # Phase1: 取得商品連結，過濾雜訊
  product_name_and_id = None
  match website:
    case 'momo':
      product_name_and_id = search_momo(query)
    case 'amazon':
      product_name_and_id = search_amazon(query)
    case _:
      print("Invalid website")
      return
  if product_name_and_id is None:
    return
  product_name_and_id = filter_result_by_llm(product_name_and_id)
  reviews = []
  ct=0
  for title, id in product_name_and_id[:limit]:
    res = Textmodel.generate_content(f"我想查詢{query}這個系列的評價，請判斷這個商品的title: {title}是所指的商品否與query為相同型號的商品，並回答yes or no，並簡單說明理由")
    if "no" in res.text or "No" in res.text or "NO" in res.text:

      continue


    match website:
      case 'momo':
        reviews.extend(get_reviews_momo(id))
      case 'shopee':
        pass
      case 'amazon':
        reviews.extend(get_reviews_amazon(id, log=False))
      case _:
        print("Invalid website")
    ct+=1
    if  len(reviews) >= k:
      break
  review_summary = Textmodel.generate_content(f"這是對商品 apple watch 的 在電商amazon上的評論:{str(reviews)}，請彙整並告訴我綜合評價").text
  return review_summary

if __name__ == "__main__":
    genai.configure(api_key='AIzaSyAY6Q1GIxBg-s5ocjPxwvjh1D0IB-nKglY')
    Textmodel = genai.GenerativeModel('gemini-1.5-flash')
    print(Textmodel)
    print("-----------------Testing amazon-----------------")
    az_r = CommentAPI(query="apple watch",Textmodel=Textmodel, website="amazon", log=0)
    print(f'get{len(az_r)} reviews from amazon')
    print(Textmodel.count_tokens(az_r))
    a = Textmodel.generate_content(f"這是對商品 apple watch 的 在電商amazon上的評論:{str(az_r)}，請彙整並告訴我綜合評價").text
    print(a)
