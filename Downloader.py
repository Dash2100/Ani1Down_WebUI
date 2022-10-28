import requests, re
from bs4 import BeautifulSoup
from flask import url_for
from urllib.parse import unquote
import os
from os import listdir, remove
from os.path import isfile, isdir, join
import json
from lxml.html import fromstring

path = "./Downloads/"
serverip = "http://127.0.0.1:5050"

def writejson(data):
    with open('data/cache.json', 'w', encoding="UTF-8") as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))

def update(utype,udata):
    data = {'data':{'update_type':utype,'data':udata}}
    requests.get(f'{serverip}/updateData',json=data)

def Download(url,cookies,name,Download_path):
    global title
    headers_cookies ={
        "accept": "*/*",
        "accept-encoding": 'identity;q=1, *;q=0',
        "accept-language": 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        "cookie": cookies,
        "dnt": '1',
        "user-agent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }
    downsize = 0
    r = requests.get(url, headers=headers_cookies, stream=True)
    file_size = round(int(r.headers['content-length'])/1024/1024,2)
    if r.status_code == 200:
        print("Downloading " + title + ' ' + name)
        with open('data/cache.json', 'r', encoding="UTF-8") as cache:
            data = json.load(cache)
        data['downloading'][title + name] = url
        writejson(data)
        update('downloading',{title+name:"0/"+str(file_size)+"MB"})
        update('getdata','')
        size_counter = 0
        with open(Download_path+name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    downsize += len(chunk)
                    size_counter += len(chunk)
                    # line = '%.2f MB / %.2f MB'
                    # info = line % (downsize / 1024 / 1024, file_size)
                    # print("Downloading " + title + ' ' + name + " " + info, end='\r')
                    if size_counter >= 6000000:
                        size_counter = 0
                        update('downloading',{title+name:str(round(downsize / 1024 / 1024,2))+"/"+str(file_size)+"MB"})
                        with open('data/cache.json', 'r', encoding="UTF-8") as cache:
                            data = json.load(cache)
                        if data['stop'] == True:
                            update('notdownloading','')
                            return("Download Cancel")
        
        #Download Complete Delete Cache
        with open('data/cache.json', 'r', encoding="UTF-8") as cache:
            data = json.load(cache)
        data['downloading'] = {}
        writejson(data)
        return("ok")
    else:
        print("Download Error: " + str(r.status_code))

def complete(state):
    update('notdownloading','')
    with open('data/cache.json', 'r', encoding="UTF-8") as f:
        json_file = json.load(f)
    json_file['status'] = False
    json_file['downloading_URL'] = ""
    json_file['stop'] = False
    writejson(json_file)
    if json_file['waiting'] != []:
        url = list(json_file['waiting'][0].values())[0]
        json_file['waiting'].pop(0)
        writejson(json_file)
        Anime(url)
    if state == "ok":
        return("Download Complete")
    if state == "Cancel":
        return("Download Cancel")

def get(url):
    global title
    r = requests.post(url,headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34"})

    soup = BeautifulSoup(r.text, 'html.parser')
    try:
        title = soup.find('h1', class_='page-title').text
    except:
        with open('data/cache.json', 'r', encoding="UTF-8") as f:
            json_file = json.load(f)
        json_file['status'] = False
        json_file['stop'] = False
        json_file['downloading_URL'] = ""
        writejson(json_file)
        return("URL Error")
    Download_path = path + title + '/'
    if not os.path.isdir(Download_path):
        os.mkdir(Download_path)
    videos = soup.find_all("video")
    
    for video in videos:
        data = {'d':unquote(video['data-apireq'])}
        r = requests.post("https://v.anime1.me/api",data=data)
        t = "https://" + str(r.text).replace('{"s":[{"src":"//','').replace('","type":"video/mp4"}]}','')
        set_cookie = r.headers['set-cookie']
        cookie_e = re.search(r"e=(.*?);", set_cookie, re.M|re.I).group(1)
        cookie_p = re.search(r"p=(.*?);", set_cookie, re.M|re.I).group(1)
        cookie_h = re.search(r"HttpOnly, h=(.*?);", set_cookie, re.M|re.I).group(1)
        cookies = 'e={};p={};h={};'.format(cookie_e, cookie_p, cookie_h)
        name = t.split('/')[-1]
        d = Download(t,cookies,name,Download_path)
        if d == "Download Cancel":
            requests.get(f"{serverip}/delani/{title}")
            return(complete('Cancel'))
        with open('data/cache.json', 'r', encoding="UTF-8") as f:
            json_file = json.load(f)
        if json_file['stop'] == True:
            json_file['status'] = False
            json_file['stop'] = False
            json_file['downloading_URL'] = ""
            writejson(json_file)
            return(complete('ok'))
    #下載完成
    return(complete('ok'))
    

def Anime(url):
    try:
        r = requests.get(url)
    except:
        return("URL Error")
    #get title
    tree = fromstring(r.content)
    title = tree.findtext('.//title').split('–')[0].rstrip()
    #get all video path
    all_path = []
    mypath = "./Downloads"
    files = listdir(mypath)
    for f in files:
        fullpath = join(mypath, f)
        if isdir(fullpath):
            all_path.append(f)
    #check if file is exist
    if title in all_path:
        return("File Exist")

    with open('data/cache.json', 'r', encoding="UTF-8") as f:
        json_file = json.load(f)
    if json_file['status'] == False:
        #Write Status True
        json_file['status'] = True
        json_file['downloading_URL'] = url
        writejson(json_file)
        #Start Download
        return get(url)
    else:
        if url in json_file['downloading_URL']:
            return("already in downloading")

        all_title = []
        for d in json_file['waiting']:
            all_title.append(list(d.values())[0])
        if url in all_title:
            return("already in queue")
        json_file['waiting'].append({title:url})
        writejson(json_file)
        return("added to queue list")

# if __name__ == '__main__':
#     Anime(sys.argv[1])