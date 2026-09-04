from playwright.sync_api import sync_playwright
from urllib.parse import urlparse,parse_qs
from urllib.parse import unquote
import subprocess
from bs4 import BeautifulSoup
import json
import base64
import requests
import uuid
import os
import time
import threading
import queue
import re

tasks=queue.Queue()
# results=queue.Queue()
progress={}
def playwright_worker():
    print("playwright working is start....")
    with sync_playwright()as p:
        broswer=p.chromium.launch(headless=True)

        print("playwright broswer is lanuch and wait your task")

        while True:
            task=tasks.get()
            if task is None:
                break
            time_start=time.perf_counter()
            url,request_id = task

            # request working start here
            urls={
                "video":None,
                "audio":None
            }
            progress[request_id] = {
                 "status": "browser",
                 "percent": 10,
                 "video_url": None,
                 "audio_url": None,
                 "audio_path":None,
                 "video_path":None,
                 "output_path":None,
                 "thumbnail": None,
                 "user_name": None,
                 "caption": None
             }
            folder=os.path.join("media","temp",request_id)
            os.makedirs(folder,exist_ok=True)
            video_path = os.path.join(folder, "video.mp4")
            audio_path = os.path.join(folder, "audio.mp4")
            output_path = os.path.join(folder, "output.mp4")
            bros_page=time.perf_counter()
            page=broswer.new_page()            
            print(f"New page: {time.perf_counter() - bros_page:.2f}s")
            pag_goto=time.perf_counter()
            # page.on("response",lambda response:log_request(response,urls,pag_goto))
            pag_goto = time.perf_counter()
            page.on("request", lambda request: log_request(request, urls,pag_goto))
            page.goto(url,wait_until="commit")
            print(f"Page goto: {time.perf_counter() - pag_goto:.2f}s")

            progress[request_id]["status"]="page_goto"
            progress[request_id]["percent"]=20
            start_wait=time.perf_counter()
            
            while not(
                urls["video"]and urls["audio"]

            ):
                if time.perf_counter() - start_wait > 10:
                    break
                page.wait_for_timeout(100)
            if not urls["audio"] or not urls["video"]:
                progress[request_id]["status"]="error"
                page.close()
                continue
            print(
             f"🎥 Video/audio wait: "
             f"{time.perf_counter() - start_wait:.2f}s"
            )
            progress[request_id]["status"]="media"
            progress[request_id]["video_url"]=urls["video"]
            progress[request_id]["audio_url"]=urls["audio"]
            progress[request_id]["audio_path"]=audio_path
            progress[request_id]["video_path"]=video_path
            progress[request_id]["output_path"]=output_path
            progress[request_id]["download_started"] = False
            progress[request_id]["percent"]=50
             # GET METADATA
            startm = time.perf_counter()
            # html=page.content()
            # soup=BeautifulSoup(html,"html.parser")

            # thumbnail = page.locator("meta",property="og:image")["content"]
            thumbnail = page.locator('meta[property="og:image"]').get_attribute("content")
            print(thumbnail)
            
            progress[request_id]["status"]="thumbnail"
            progress[request_id]["thumbnail"]=thumbnail
            progress[request_id]["percent"]=60
            # discription = page.locator("meta",property="og:description")["content"]
            discription = page.locator('meta[property="og:description"]').get_attribute("content")
            print(discription)
            print(f"Metadata: {time.perf_counter() - startm:.3f}s")
            start = time.perf_counter()
            user_match = re.search(r'- (.*?) on ', discription)

            if user_match:
               user_name = user_match.group(1)
               print("Username regex:", time.perf_counter() - start)
            else:
               user_name = None
            progress[request_id]["status"]="user_name"
            progress[request_id]["user_name"]=user_name
            progress[request_id]["percent"]=80
            start = time.perf_counter()
            caption_match = re.search(r': "(.*)"', discription, re.DOTALL)

            if caption_match:
               caption = caption_match.group(1)
               print("Caption regex:", time.perf_counter() - start)
            else:
               caption = None  
               print("CAPTION MATCH FAILED")
            progress[request_id]["status"]="complete"
            progress[request_id]["caption"]=caption
            progress[request_id]["percent"]=100

            page.close()
            print("❌ Page closed")
            print(
               f"🏁 Final time: "
               f"{time.perf_counter() - time_start:.2f}s"
             )
worker = threading.Thread(
     target=playwright_worker,
     daemon=True
)
worker.start()
            
def get_video(url):
    URL=url
    request_id=uuid.uuid4().hex
    tasks.put((URL,request_id))
    return request_id


def log_request(response , urls,pag_goto):
    filter_start = time.perf_counter()
    # print("CALLED FROM:", type(response).__name__)
    data=response.url
    if ".mp4" not in data:
       return
    params=parse_qs(urlparse(data).query)
    if "efg" not in params:
       print("\n efg not found")
       return
    raw_efg=unquote(params["efg"][0])
    try:
         decode=base64.b64decode(raw_efg).decode("utf-8")
        #  print(decode)
         efg=json.loads(decode)
    except Exception as e:
        print(f"\n❌ Decode Error: {e}")
        return 
    tag=efg.get("vencode_tag","")

    if "audio" in tag.lower()and urls["audio"] is None:
        url=data.split("&bytestart=")[0]
        urls["audio"]=url
        # download(urls["audio"],audio_path)
        print(urls["audio"])
        print("this audio url") 
        print(f"🎵 AUDIO FOUND: {time.perf_counter() - pag_goto:.3f}s")
        print(f"🎵 Audio filter: {time.perf_counter() - filter_start:.6f}s")

    elif"dash_baseline" in tag.lower() and urls["video"] is None:
        clean_url = data.split("&bytestart=")[0]
        urls["video"]= clean_url
        # download(urls["video"],vedio_path)
        print(urls["video"])
        print("this vedio url") 
        print(f"🎥 VIDEO FOUND: {time.perf_counter() - pag_goto:.3f}s")
        print(f"🎥 Video filter: {time.perf_counter() - filter_start:.6f}s")
        
def is_instagram_reel(url):
    try:
        parsed = urlparse(url)

        if parsed.scheme != "https":
            return False

        if parsed.netloc not in ["instagram.com", "www.instagram.com"]:
            return False

        if not parsed.path.startswith("/reel/"):
            return False

        return True

    except Exception:
        return False
