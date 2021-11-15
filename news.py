import requests
import json
import sys
import re
import time
from bs4 import BeautifulSoup
from pathlib import Path

def run(cmd, lang, additional):    

    cache_path = '/tmp/news-cache/'
    if not Path(cache_path).exists():
        Path(cache_path).mkdir()

    if cmd == 'list':
        links = []
        titles = []

        ts = time.time()
        ts = ts // 1800 * 1800
        key = lang+'-'+str(ts)
        path = Path(cache_path+key)

        if path.exists():
            file = path.open(mode='r')
            js = file.read()
            file.close()
            rs = json.loads(js)
            links = rs['links']
            titles = rs['titles']
        else:
            if lang == 'nhk' or lang == 'nhk-more':
                if lang == 'nhk':
                    res = requests.get('https://www3.nhk.or.jp/news/json16/syuyo.json')
                else:
                    res = requests.get('https://www3.nhk.or.jp/news/json16/new_001.json')
                content = json.loads(res.text)
                items = content['channel']['item']
                for item in items:
                    links.append(item['link'])
                    titles.append(item['title'])
            elif lang == 'onu-es' or lang == 'onu-fr' or lang == 'onu-ru' or lang == 'onu-pt' or lang == 'onu-sw':
                sub = lang[4:]
                res = requests.get('https://news.un.org/' + sub)
                soup = BeautifulSoup(res.text, 'html.parser')
                tags = soup.find_all('a')
                for tag in tags:
                    r = tag.get('href')
                    if r is not None and r.startswith('/' + sub +'/story') and len(tag.get_text().strip()) > 0:
                        href = tag.get('href')
                        links.append(href)
                        titles.append(tag.get_text().strip())
            elif lang == 'rtve':
                res = requests.get('https://www.rtve.es/')
                soup = BeautifulSoup(res.text, 'html.parser')
                tags = soup.find_all('a')
                for tag in tags:
                    r = tag.get('href')
                    if r is not None and (r.startswith('https://www.rtve.es/noticias/') and 'more' not in sys.argv or r.startswith('https://www.rtve.es/') and 'more' in sys.argv ) and r.endswith('.shtml') and len(tag.get_text().strip()) > 0:
                        href = tag.get('href')
                        links.append(href)
                        titles.append(tag.get_text().strip())
            elif lang == 'fr24' or lang == 'fr24-es':
                headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
                if len(lang)<=4:
                    sub = 'fr'
                else:
                    sub = lang[5:]
                res = requests.get('https://www.france24.com/' + sub + '/', headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')
                tags = soup.find_all('a')
                links = []
                for tag in tags:
                    r = tag.get('href')
                    if r is not None and r.startswith('/' + sub + '/') and len(r)>50 and len(tag.get_text()) > 0:
                        href = tag.get('href')
                        links.append(href)
                        titles.append(tag.get_text().strip())
            elif lang == 'detik':
                res = requests.get('https://news.detik.com/?tag_from=wp_firstnav_detikNews')
                soup = BeautifulSoup(res.text, 'html.parser')
                tags = soup.find_all('a')
                links = []
                for tag in tags:
                    r = tag.get('href')
                    if r is not None and r.startswith('https://news.detik.com/berita') and '/d-' in r and len(tag.get_text().strip()) > 0:
                        href = tag.get('href')
                        links.append(href)
                        titles.append(tag.get_text().strip())
            elif lang == 'bh-my':
                res = requests.get('https://www.bharian.com.my/api/articles?sttl=true&page_size=8')
                items = json.loads(res.text)
                for item in enumerate(items):
                    links.append(item['internal_url'])
                    titles.append(item['title'])
            elif lang == 'bh-sg':
                res = requests.get('https://www.beritaharian.sg/')
                soup = BeautifulSoup(res.text, 'html.parser')
                tags = soup.find_all('a')
                for tag in tags:
                    r = tag.get('href')
                    if r is not None and len(r.split('/'))==3 and len(tag.get_text()) > 0:
                        href = tag.get('href')
                        links.append(href)
                        titles.append(tag.get_text().strip())
            elif lang == 'milenio':
                res = requests.get('https://www.milenio.com')
                soup = BeautifulSoup(res.text, 'html.parser')
                tags = soup.find_all('a')
                for tag in tags:
                    r = tag.get('href')
                    title = tag.find('h2', {'data-camus-title': ''})
                    if r is not None and r.startswith('/') and title is not None and len(tag.get_text()) > 0:
                        href = tag.get('href')
                        links.append(href)
                        titles.append(tag.get_text().strip())
            else:
                print("unknown website")

            if len(titles)>0 and len(links)>0:
                rs = {
                    'titles' : titles,
                    'links' : links,
                }
                js = json.dumps(rs)
                file = path.open(mode='w')
                file.write(js)
                file.close()
        
        typ = additional
        if typ == 'url':
            for i, link in enumerate(links):
                print("{0:<3}".format(i+1) + " [" + link + "] ")
        elif typ == 'title':
            for i, title in enumerate(titles):
                print("{0:<3}".format(i+1) + " " + title)
        else:
            for i, title in enumerate(titles):
                print("{0:<3}".format(i+1) + " [" + links[i] + "] " + title)   

    if cmd == 'show':
        url = additional
        tit = ''
        pargs = []

        key = lang + '-' + url.replace('/','.')
        path = Path(cache_path+key)

        if path.exists():
            file = path.open(mode='r')
            js = file.read()
            file.close()
            rs = json.loads(js)
            tit = rs['tit']
            pargs = rs['pargs']
        else:
            if lang == 'nhk' or lang == 'nhk-more':
                res = requests.get('https://www3.nhk.or.jp/news/' + url)
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'html.parser')
                title = soup.find('h1', {'content--title'}).find('span')
                tit = title.get_text().strip()
                summary = soup.find('p', {'class':'content--summary'}).get_text().strip()
                if summary is not None:
                    pargs.append(summary)
                sections = soup.find('div', {'class': 'content--detail-more none-mobile'}).find_all('section')
                for section in sections:
                    for paragraph in section.find_all('h2', {'class': 'body-title'}):
                        text = paragraph.get_text("\n").strip()
                        if text is not None and text != '':
                            pargs.append(text)
                    for paragraph in section.find_all('div', {'class': 'body-text'}):
                        text = paragraph.get_text("\n").strip()
                        if text is not None and text != '':
                            pargs.append(text)
            elif lang == 'onu-es' or lang == 'onu-fr' or lang == 'onu-ru' or lang == 'onu-pt' or lang == 'onu-sw':
                res = requests.get('https://news.un.org' + url)
                soup = BeautifulSoup(res.text, 'html.parser')
                title = soup.find('h1', {'class': 'story-title'})
                tit = title.get_text().strip()
                paragraphs = soup.find('div', {'class': 'field-type-paragraphs'}).find_all('p')
                for paragraph in paragraphs:
                    text = paragraph.get_text().strip()
                    if text is not None:
                        pargs.append(text)
            elif lang == 'rtve':
                res = requests.get(url)
                soup = BeautifulSoup(res.text, 'html.parser')
                title = soup.find('span', {'class': 'maintitle'})
                tit = title.get_text().strip()
                paragraphs = soup.find('div', {'class': 'mainContent hid_email'}).find_all('p')
                for paragraph in paragraphs:
                    text = paragraph.get_text().strip()
                    if text is not None and text != '':
                        pargs.append(text)
            elif lang == 'fr24' or lang == 'fr24-es':
                res = requests.get('https://www.france24.com'+url, headers=headers)
                soup = BeautifulSoup(res.text, 'html.parser')
                title = soup.find('h1', {'class': 't-content__title a-page-title'})
                tit = title.get_text().strip()
                brief = soup.find('p', {'class': 't-content__chapo'})
                pargs.append(brief)
                paragraphs = soup.find('div', {'class': 't-content__body'}).find_all('p')
                for paragraph in paragraphs:
                    text = paragraph.get_text().strip()
                    if text is not None and text != '':
                        pargs.append(text)
            elif lang == 'detik':
                res = requests.get(url)
                soup = BeautifulSoup(res.text, 'html.parser')
                title = soup.find('h1', {'class': 'detail__title'})
                tit = title.get_text().strip()
                pages = soup.find('div', {'class': 'detail__anchor'}).find_all('a')
                for page in pages:
                    href = page.get('href')
                    res = requests.get(url)
                    soup = BeautifulSoup(res.text, 'html.parser')
                    paragraphs = soup.find('div', {'class': 'detail__body-text itp_bodycontent'}).find_all('p')
                    for paragraph in paragraphs:
                        text = paragraph.get_text().strip()
                        if text is not None:
                            pargs.append(text)
            elif lang == 'bh-my':
                es = requests.get('https://www.bharian.com.my'+url)
                res.encoding = 'utf-8'
                soup = BeautifulSoup(res.text, 'html.parser')
                article = soup.find('article-component')
                article_json = json.loads(article.get(':article'))
                tit = article_json['title']
                soup = BeautifulSoup(article_json['body'], 'html.parser')
                paragraphs = soup.find_all('p')
                for paragraph in paragraphs:
                    text = paragraph.get_text().strip()
                    if text is not None and text != '':
                        pargs.append(text)
            elif lang == 'bh-sg':
                res = requests.get('https://www.beritaharian.sg'+url)
                soup = BeautifulSoup(res.text, 'html.parser')
                title = soup.find('h1', {'class': 'article-headline mb-4'})
                tit = title.get_text().strip()
                paragraphs = soup.find('div', {'class': 'odd field-item article'}).find_all('p')
                for paragraph in paragraphs:
                    text = paragraph.get_text().strip()
                    if text is not None and text != '':
                        pargs.append(text)
            elif lang == 'milenio':
                res = requests.get('https://www.milenio.com'+url)
                soup = BeautifulSoup(res.text, 'html.parser')
                title = soup.find('div', {'class': 'bg-content'})
                tit = title.find('span').get_text()
                paragraphs = soup.find('div', {'id': 'content-body'}).find_all(re.compile('^((p)|(blockquote)|(h2)|(li))$'))
                for paragraph in paragraphs:
                    text = paragraph.get_text().strip()
                    if text is not None and len(text)>0:
                        pargs.append(text)
            if len(pargs)>0 and len(tit)>0:
                rs = {
                    'tit' : tit,
                    'pargs' : pargs,
                }
                js = json.dumps(rs)
                file = path.open(mode='w')
                file.write(js)
                file.close()

        print(tit)
        print()
        for parg in pargs:
            print(parg)
            print()

def help():
    print(['nhk','nhk-more','fr24','fr24-es','rtve','detik','bh-sg','bh-my','milenio','onu-es','onu-sw','onu-pt','onu-ru','onu-fr'])

if len(sys.argv)<=1:
    help()
    exit()

lang = sys.argv[1]
if lang == 'help':
    help()
    exit()
    
cmd = sys.argv[2]
additional = ''
if len(sys.argv) > 3:
    additional = sys.argv[3]

run(cmd, lang, additional)