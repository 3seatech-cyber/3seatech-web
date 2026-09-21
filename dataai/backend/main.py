import os, secrets
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext

APP_ORIGIN=os.getenv("DATAAI_ORIGIN","https://data.3seatech.com")
ADMIN_USER=os.getenv("DATAAI_ADMIN_USER","")
ADMIN_HASH=os.getenv("DATAAI_ADMIN_PASSWORD_HASH","")
if not ADMIN_USER or not ADMIN_HASH:
    print("WARNING: configure DATAAI_ADMIN_USER and DATAAI_ADMIN_PASSWORD_HASH before production login.")

pwd=CryptContext(schemes=["bcrypt"],deprecated="auto")
sessions={}
app=FastAPI(title="3SeaTech DataAI API",version="1.0.0")
app.add_middleware(CORSMiddleware,allow_origins=[APP_ORIGIN],allow_credentials=True,allow_methods=["GET","POST","OPTIONS"],allow_headers=["Content-Type","Authorization"])

class Login(BaseModel):
    username:str
    password:str

@app.get("/health")
def health():
    return {"status":"ok","service":"3seatech-dataai","utc":datetime.now(timezone.utc).isoformat()}

@app.post("/api/auth/login")
def login(data:Login,response:Response):
    if not ADMIN_USER or not ADMIN_HASH or data.username!=ADMIN_USER or not pwd.verify(data.password,ADMIN_HASH):
        raise HTTPException(401,"Credenciales incorrectas")
    token=secrets.token_urlsafe(32); sessions[token]={"user":data.username,"role":"admin"}
    response.set_cookie("dataai_session",token,httponly=True,secure=True,samesite="lax",path="/",max_age=28800)
    return {"ok":True,"role":"admin","redirect":"/dashboard.html"}

@app.get("/api/auth/me")
def me(request:Request):
    s=sessions.get(request.cookies.get("dataai_session",""))
    if not s: raise HTTPException(401,"No autenticado")
    return s

@app.post("/api/auth/logout")
def logout(request:Request,response:Response):
    sessions.pop(request.cookies.get("dataai_session",""),None)
    response.delete_cookie("dataai_session",path="/")
    return {"ok":True}
