from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from yt_dlp import YoutubeDL
from django.conf import settings
import assemblyai as aai
# Create your views here.
@login_required(login_url="/login")
def home(request):
    return render(request,"home.html")


def signUp(request):
    if request.method=="POST":
        form=RegistrationForm(request.POST)
        if form.is_valid():
            user=form.save()
            login(request,user)
            return redirect("home")
            
    else:
        form=RegistrationForm()
    return render(request,"registration/sign_up.html",{"form":form})

@csrf_exempt
def generate_blog(request):
    if request.method=="POST":
        
        try:
            data=json.loads(request.body)
            yt_link=data["link"]
            text=get_transcription(yt_link)
            
            
            return JsonResponse({"content":text})
        except Exception as er:
            print(er)
            
    else:
        return JsonResponse({"error":"Invalid Request Method"},status=405)

def get_title(url):
    options={
        "quiet":True,
        "no_warnings":True
    }
    with YoutubeDL(options) as ytdl:
        try:
            info=ytdl.extract_info(url,download=False)
            return info.get("title","No Title Found")
            
        except Exception as er:
            print(er)
    
# def hook(d):
#     if d["status"]=="finished":
#         print(f"Downloaded FILE:{d["filename"]}")
def download_audio(url,out_path=settings.MEDIA_ROOT):
    def hook(d):
        if d['status'] == 'finished':
            global audfile
            audfile=d["info_dict"]["filepath"] # File path of the saved file
    options={
        "format":"bestaudio/best",
        "outtmpl":f"{out_path}/%(title)s.%(ext)s",
        "postprocessor_hooks":[hook],
        # 'progress_hooks': [hook],
        "ffmpeg_location":'D:\\ffmpeg-2025-01-20-git-504df09c34-essentials_build\\ffmpeg-2025-01-20-git-504df09c34-essentials_build\\bin',
        "postprocessors":[{
            "key":"FFmpegExtractAudio",
            "preferredcodec":"mp3",
            "preferredquality":"192",
        }],
        "quiet":False
        
    }
    with YoutubeDL(options) as ytdl:
        try:
           return ytdl.download([url])
            
            
            
        except Exception as er:
            print(er)
    
def get_transcription(link):
    download_audio(link) 
    aai.settings.api_key="44b66af42f64486e8bd9dd61501ff060"
    transcriber=aai.Transcriber()
    transcript=transcriber.transcribe(audfile)
    return transcript.text

def create_post(request):
    return render(request,"index.html")

def detail_post(request):
    return render(request,"blog_details.html")