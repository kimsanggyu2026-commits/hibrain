import requests
from bs4 import BeautifulSoup
import os

# 환경 변수 로드
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID_JOB") # 채용 전용 채널 ID

# 하이브레인넷 사학 카테고리
URL = "https://www.hibrain.net/recruitment/categories/MJR/categories/H/categories/H02/recruits?sortType=SORTDTM&displayType=TIT&listType=ING&limit=25&siteid=1&page=1"
DB_FILE = "last_link_hibrain.txt"

# 🌟 역사학 관련 키워드 필터링 (여기에 포함된 단어가 제목에 있어야만 알림을 보냅니다)
KEYWORDS = ["사학", "역사", "한국사", "동양사", "서양사", "고고학", "미술사", "박물관", "기록물", "문화재", "학예"]

def send_telegram(title, link):
    msg = f"<b>🎓 역사학 채용 새 소식</b>\n\n{title}\n\n<a href='{link}'>공고 확인하기</a>"
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}
    try:
        requests.post(url, data=params, timeout=10)
    except:
        pass

def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        res = requests.get(URL, headers=headers, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        last_link = ""
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r") as f:
                last_link = f.read().strip()

        new_posts = []
        # 하이브레인넷 목록 추출
        items = soup.select('ul.recruitment_list_type_tit li')
        
        for item in items:
            title_tag = item.select_one('span.title a')
            if not title_tag: continue
            
            title = title_tag.get_text(strip=True)
            link = "https://www.hibrain.net" + title_tag['href']
            
            if link == last_link:
                break
            
            # 🌟 필터링: 제목에 키워드가 하나라도 포함되어 있는지 확인
            if any(kw in title for kw in KEYWORDS):
                new_posts.append({'title': title, 'link': link})
        
        # 오래된 공고부터 알림 발송
        for post in reversed(new_posts):
            send_telegram(post['title'], post['link'])
            print(f"    [발송] {post['title']}")

        # 최신 링크 저장
        if new_posts:
            with open(DB_FILE, "w") as f:
                f.write(new_posts[0]['link'])

    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    main()