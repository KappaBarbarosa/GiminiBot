import requests
from bs4 import BeautifulSoup
import json
import os
import xml.etree.ElementTree as ET
NEWS_API_KEY = 'c900b5c5bded495b8a00135c6dcf0267'

def GetHeadlinesSummaryByCountry(country,range=10):

    url = (f'https://newsapi.org/v2/top-headlines?'
        'country=tw&'
        'sortBy=publishedAt&'
        'apiKey=c900b5c5bded495b8a00135c6dcf0267')
    response = requests.get(url).json()
    # with open('headkines.json', 'r', encoding='utf-8') as f:
    #     response = json.load(f)
    # print(response)
    if response['status'] != 'ok':
        print("Error: Unable to fetch news data from the API")
        return
    articles = response['articles']
    print(len(articles))
    extract_full_text_from_API(articles,range)

def GetInquiredNewsContent(query, range,force_search):
    url = f'https://news.google.com/rss/search?q={query}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant'
    response = requests.get(url)
    
        # Print the title, link, and publication date of each news item
    if os.path.exists(f'{query}_response.json') == False or force_search == True:
       if response.status_code == 200:
        # Parse the XML content
            root = ET.fromstring(response.content)
            articles=   []
            for item in root.findall('./channel/item'):
                article = {
                    'title': item.find('title').text,
                    'url': item.find('link').text,
                    'pubDate': item.find('pubDate').text
                }
                articles.append(article)
            Result = {
                'query': query,
                'articles': articles,
                'cur':0
            }
            Result = json.dumps(Result, ensure_ascii=False)
            with open(f'{query}_response.json', 'w+', encoding='utf-8') as f:
                f.write(Result)
       else:
            raise Exception("錯誤：無法從API獲取新聞資料")
    else:
        with open(f'{query}_response.json', 'r', encoding='utf-8') as f:
            Result = json.load(f)
    # print(Result)
    cur = Result['cur']    
    articles = Result['articles']

    if len(articles) == 0:
        raise Exception("錯誤：找不到相關新聞")
    
    count,responses = extract_full_text_from_API(articles,cur,range)
    Result['cur'] = cur+count
    Result = json.dumps(Result, ensure_ascii=False)
    with open(f'{query}_response.json', 'w+', encoding='utf-8') as f:
        f.write(Result)
    return responses


def verify_autor_group(author,source):
    if author == None :
        return 'other'
    if author == 'TVBS':
        return 'tvbs'
    else:
        return 'p'
def extract_full_text_from_API(articles,cur,range=10):
    responses=[]
    count=0
    for i,article in enumerate(articles) :
        if i < cur:
            continue
        if range == count:
            break
        response = requests.get(article['url'])
        soup = BeautifulSoup(response.text, 'html.parser')

        if 'TVBS' in article['title'] :
            script_tag = soup.find('script', type='application/ld+json')

            # 獲取 script 標籤內的 JSON 內容
            json_content = script_tag.string

            # 解析 JSON 內容
            article_info = json.loads(json_content)

            # 獲取 articleBody 的內容
            article_body = article_info.get("articleBody", "")
            responses.append({
                'title':article['title'],
                'content':article_body,
                'url':article['url']
            })
            count+=1
        else: 
            content = soup.find_all('p')
            if len(content) == 0:
                print("No content found")
                continue
            responses.append({
                'title':article['title'],
                'content':content,
                'url':article['url']
            })
            count+=1
            
    return count, responses
        
if __name__ == '__main__':
    GetInquiredNewsContent('生成式AI',range=3,force_search=False)