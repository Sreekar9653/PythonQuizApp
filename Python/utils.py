import re
import streamlit as st
import time
from ollama import chat
import json
from supabase import Client, create_client
import requests
from bcrypt import hashpw as encrypt, checkpw, gensalt

db=st.secrets["suprabase_api_key"]
srole=st.secrets["srole"]
url=st.secrets["suprabase_url"]
supabase:Client = create_client(url, srole)

# ---------------- Login Setup starts ----------------
def adduser(name,user,password):
    data = {
        "name": name,
        "username": user,
        "password": str(encrypt(password.encode(), gensalt()))[2:-1]
    }

    try:response = supabase.table("Users").insert(data).execute()
    except Exception as e: print(str(e))
    else:userdata[user]={"name":name,"password":password,"usertype":"candidate","test_status":"Not yet started"}

def getusers():
    global userdata,users
    try:
        users = supabase.table("Users").select("username,name,password,usertype,test_status").execute().data
        userdata={i.pop("username"):i for i in userdata}
    except Exception as e:
        print(str(e))
        userdata=[]
    return userdata 

def checkuser(password,username):
    return checkpw(password.encode(),getusers()[username]["password"].encode())

# ---------------- Test Setup starts ----------------
def query(prompt):
    try:
        response = chat(model="mistral:7b", 
                    messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"]
    except Exception as e:
        return str(e)
    
def findquestions(context):
    try:
        prompt=open("Prompts/generatequests.txt","r",encoding="utf-8").read().replace("<context>",str(context))
        return query(prompt)
    except Exception as e:
        print(str(e))
        return 0

def evaluate(username,context,time_rem):
    try:
        questions,answers=list(zip(*context))
        context=[i+[j] for i,j in zip(context,time_rem)]
        prompt=open("Prompts/evaluate.txt","r",encoding="utf-8").read().replace("<context>",str(context))
        result=query(prompt)
        score=re.findall(r"(\d+)/10",result)
        if score: score=int(score[0])
        data={"uid":username,
            "questions":questions,
            "answers":answers,
            "time_taken":time_rem,
            "feedback":result,
            "score":score
            }
        response = supabase.table("Tests").insert(data.execute())
        return result
    except Exception as e:
        print(str(e))
        return 0
    
# ---------------- Admin Setup ends ----------------
def getresults():
    try:
        tests = supabase.table("Tests").select("*").execute().data
        return [users,tests]
    except Exception as e:
        print(str(e))

        return 0
