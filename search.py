import http.client
import json
import re
import requests
from parameters import safety_config
import os
def google_search(query, num_results):
    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        "q": query,
        "gl": "tw",
        "hl": "zh-tw",
        "num": num_results
    })
    headers = {
        'X-API-KEY': os.getenv("SEARCH_KEY"),
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    
    if res.status != 200:
        raise Exception(f"Google Search API request failed with status {res.status}")
    
    results = res.read().decode("utf-8")
    results = json.loads(results)['organic']

    return [
        {
            "title": result["title"],
            "description": result['snippet'],
            "url": result['link']
        }
        for result in results
    ]

def get_web_content(url):
    response = requests.get(f'https://r.jina.ai/{url}')
    
    if response.status_code != 200:
        return "idk"
    
    content = response.text
    content = re.sub(r'\[!\[Image.*?\)\]\(.*?\)', '', content)
    content = re.sub(r'!\[Image.*?\)', '', content)
    
    return content

def summarize_content(content, query, chat):
    sample = (f"這是對 query: {query} 的 Google search 結果的網頁 HTML 訊息:\n{content}\n"
              "請你根據這些網頁內容，擷取與 query 相關的資訊並做摘要，如果內容和 query 無相關，請說 'idk'")
    summary = chat.send_message(sample, safety_settings=safety_config).text
    return summary

def SearchAPI(query,Textmodel, k=3, n=10):
    results = google_search(query, n)
    chat = Textmodel.start_chat()
    contents = []

    for result in results:
        content = get_web_content(result['url'])
        
        if "idk" in content:
            continue
        
        summary = summarize_content(content, query, chat)
        if "idk" not in summary:
            contents.append(summary)
        
        if len(contents) == k:
            break
    final_summary = chat.send_message(f"你是一個專業的市場趨勢分析師，現在請你根據這些資訊，對{query}這個問題進行完整答覆", safety_settings=safety_config).text
    
    return "success", final_summary.replace("*", "")

if __name__ == "__main__":
    contents = SearchAPI("Iphone15 評價", 3, 10)