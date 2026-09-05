from django.shortcuts import render
import json
from pathlib import Path
import os
from urllib.parse import urlparse
import time
import shutil
import subprocess
import requests
import threading
from django.http import FileResponse
from django.http import JsonResponse
from .service.instagram import get_video
from .service.instagram import progress

metadata = {}
# Create your views here.
def download(request):
    return render(request,"downloder.html")

def downlod_vedio(request):
   data = json.loads(request.body)
   url=data["url"]
   uid=data.get("old_uid")
   if uid:
       folder=os.path.join("media","temp",uid)
       if os.path.exists(folder):
          shutil.rmtree(folder)
   print (url)
   if not is_instagram_reel(url):
    return JsonResponse({
        "error": "Invalid Instagram Reel URL"
    }, status=400)
   result=get_video(url)
   return JsonResponse({
    "video_id": result
})





def serve_vedio(request, video_id): 
    folder = os.path.join("media", "temp", video_id) 
    video_path = os.path.join(folder, "output.mp4") 

    return FileResponse( 
        open(video_path, "rb"), 
        as_attachment=True, 
        filename="video.mp4" 
    )






def preview_video(request,video_id):
    folder= os.path.join("media","temp",video_id)
    vedio_path=os.path.join(folder,"output.mp4")
    return FileResponse(
        open(vedio_path,"rb"),
        as_attachment=False,
        filename="video.mp4"
    )






def video_status(request, video_id):
    data=progress.get(video_id)
    if data is None:
        return JsonResponse({"error":"invalid"},status=404)
    if data.get("merge_status")=="ready":
        return JsonResponse({"status":"ready"})
    
    return JsonResponse({"status": "processing"})




def process_video(result):
    uid=result["uid"]
    metadata[uid] = {
    "duration": None,
    "resolution": None,
    "size": None,
    }
    if not result["video_url"] or not result["audio_url"]:
        progress[uid]["merge_status"] = "failed"
        return
    download_serve(result["video_url"], result["video_path"])
    download_serve(result["audio_url"], result["audio_path"])
    output=merge(
        result["output_path"],
        result["audio_path"],
        result["video_path"],
        
    )
    if output:

        progress[uid]["merge_status"]="ready"
        info=get_video_info(output)
        print(info)
        metadata[uid]["duration"] = info["duration"]
        metadata[uid]["resolution"] = info["resolution"]
        metadata[uid]["size"] = info["size"]
        metadata[uid]["status"]= "ready"
def meta_view(request,uid):
    data=metadata.get(uid)
    if not data:
        return JsonResponse({
            "status": "processing"
        })

    return JsonResponse(data)




def download_serve(url,file_name):
     r=requests.get(url , stream=True)
     with open(file_name,"wb")as p:
         for chunk in r.iter_content(1024*1024):
             if chunk:
                 p.write(chunk)






def merge(output_path,audio_path,video_path,):
    command = [
     "ffmpeg",
     "-i", video_path,
     "-i", audio_path,
     "-c:v", "copy",
     "-c:a", "aac",
     "-y",
     output_path
    ]
    result=subprocess.run(command)
    if result.returncode == 0:
      print("✅ Merge Successful")
      return output_path 
    
    else:
     print("❌ Merge Failed")
     return None




def progresing (request,uid):
    data= progress.get(uid)
    if data["status"]=="error":
        return JsonResponse({
            "error":"vedio are not found on server"
        })
    if data["status"]=="complete" and not data["download_started"]:
       data["download_started"]=True
       result={
           "uid":uid,
           "audio_url":data["audio_url"],
           "video_url":data["video_url"],
           "audio_path":data["audio_path"],
           "video_path":data["video_path"],
           "output_path":data["output_path"]
       }
       threading.Thread(
        target=process_video,
        args=(result,),
        daemon=True
        ).start()
    return JsonResponse(data)
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
def get_video_info(video_path):

    result = subprocess.run([
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        video_path
    ], capture_output=True, text=True)

    data = json.loads(result.stdout)
    print("json data",data)

    video = next(
        stream for stream in data["streams"]
        if stream["codec_type"] == "video"
    )

    return {
        "duration": float(data["format"]["duration"]),
        "resolution": f'{video["width"]}x{video["height"]}',
        "size": f'{int(data["format"]["size"]) / (1024 * 1024):.2f} MB'
    }
