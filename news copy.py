import requests
from bs4 import BeautifulSoup
import json
import os

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
    url = f'https://newsapi.org/v2/everything?q={query}&sortBy=publishedAt&apiKey={NEWS_API_KEY}'

    if os.path.exists(f'{query}_response.json') == False or force_search == True:
        response = requests.get(url).json()
        response['query'] = query
        cur = response['cur'] = 0
        response['range'] = range
        response_text = json.dumps(response, ensure_ascii=False)
        with open(f'{query}_response.json', 'w+', encoding='utf-8') as f:
            f.write(response_text)
    else:
        with open(f'{query}_response.json', 'r', encoding='utf-8') as f:
            response = json.load(f)
            cur = response['cur']
        
    articles = response['articles']

    if response['status'] != 'ok':
        raise Exception("錯誤：無法從API獲取新聞資料")
        return  None    
    if len(response['articles']) == 0:
        raise Exception("錯誤：找不到相關新聞")
    
    count,responses = extract_full_text_from_API(articles,cur,range)
    response['cur'] = cur+count
    response_text = json.dumps(response, ensure_ascii=False)
    with open(f'{query}_response.json', 'w+', encoding='utf-8') as f:
        f.write(response_text)
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
        group = verify_autor_group(author=article['author'],source=article['source']['name'])
        response = requests.get(article['url'])
        soup = BeautifulSoup(response.text, 'html.parser')

        if group == 'p':
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
        elif group == 'tvbs':
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
    return count, responses
        
