from django.shortcuts import render,redirect
from .forms import *
from django.contrib.auth import login,logout,authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import os
from yt_dlp import YoutubeDL
from django.conf import settings
import assemblyai as aai
from groq import Groq
from .models import *

# Create your views here.
@login_required(login_url="/login")
def home(request):
    posts=blog_post.objects.all()
    return render(request,"home.html",{"posts":posts})


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
            get_transcription(yt_link)
            title=get_title(yt_link)
            text=get_article(article)
            post=blog_post.objects.create(user=request.user,yt_Title=title,yt_url=yt_link,generated_content=text)
            post.save()
            
            if text:
                return JsonResponse({"content":text,"title":title})
            else:
                raise ValueError 
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
    aai.settings.api_key="<API KEY>"
    transcriber=aai.Transcriber()
    transcript=transcriber.transcribe(audfile)
    global article 
    article=transcript.text
    

def get_article(article):
    
    client = Groq(
    api_key="<API KEY>"
    )
    prompt = f"Based on the following transcript from a YouTube video, write a comprehensive blog article, write it based on the transcript, but dont make it look like a youtube video, make it look like a proper blog article:\n\n{article}\n\nArticle:"
    chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": prompt,
        }
    ],
    model="llama-3.3-70b-versatile",
        )
    return chat_completion.choices[0].message.content.strip()
    
def create_post(request):
    return render(request,"index.html")

def detail_post(request,id):
    post=blog_post.objects.get(id=id)
    return render(request,"blog_details.html",{"post":post})
