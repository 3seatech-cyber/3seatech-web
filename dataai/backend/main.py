import os, secrets, sqlite3, json, csv, io, statistics
from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException, Response, Request, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
import pandas as pd

BASE=Path(__file__).resolve().parent
DATA=BASE/"data"; UPLOADS=BASE/"uploads"; KNOWLEDGE=BASE/"knowledge"
for p in (DATA,UPLOADS,KNOWLEDGE): p.mkdir(exist_ok=True)
DB=DATA/"dataai.db"
ORIGIN=os.getenv("DATAAI_ORIGIN","https://data.3seatech.com")
ADMIN_USER=os.getenv("DATAAI_ADMIN_USER","")
ADMIN_HASH=os.getenv("DATAAI_ADMIN_PASSWORD_HASH","")
pwd=CryptContext(schemes=["bcrypt"],deprecated="auto")
sessions={}; sockets=set()
app=FastAPI(title="3SeaTech DataAI API",version="2.0.0")
app.add_middleware(CORSMiddleware,allow_origins=[ORIGIN],allow_credentials=True,allow_methods=["GET","POST","DELETE","OPTIONS"],allow_headers=["Content-Type","Authorization"])

def db():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS uploads(id INTEGER PRIMARY KEY,filename TEXT,kind TEXT,size INTEGER,rows INTEGER,columns INTEGER,created_at TEXT,user TEXT)""")
    c.commit(); return c

def session(req):
    s=sessions.get(req.cookies.get("dataai_session",""))
    if not s: raise HTTPException(401,"No autenticado")
    return s

async def broadcast(event,payload):
    dead=[]
    for ws in list(sockets):
        try: await ws.send_json({"event":event,"data":payload})
        except: dead.append(ws)
    for ws in dead: sockets.discard(ws)

class Login(BaseModel): username:str; password:str

@app.get("/health")
def health():
    return {"status":"ok","service":"3seatech-dataai","version":"2.0.0","utc":datetime.now(timezone.utc).isoformat()}

@app.post("/api/auth/login")
def login(data:Login,response:Response):
    if not ADMIN_USER or not ADMIN_HASH or data.username!=ADMIN_USER or not pwd.verify(data.password,ADMIN_HASH): raise HTTPException(401,"Credenciales incorrectas")
    token=secrets.token_urlsafe(32); sessions[token]={"user":data.username,"role":"admin"}
    response.set_cookie("dataai_session",token,httponly=True,secure=True,samesite="lax",path="/",max_age=28800)
    return {"ok":True,"role":"admin","redirect":"/dashboard.html"}

@app.get("/api/auth/me")
def me(request:Request): return session(request)

@app.post("/api/auth/logout")
def logout(request:Request,response:Response):
    sessions.pop(request.cookies.get("dataai_session",""),None); response.delete_cookie("dataai_session",path="/"); return {"ok":True}

@app.get("/api/stats")
def stats(request:Request):
    session(request); c=db()
    n=c.execute("select count(*) n from uploads").fetchone()["n"]; rows=c.execute("select coalesce(sum(rows),0) n from uploads").fetchone()["n"]
    last=c.execute("select created_at from uploads order by id desc limit 1").fetchone()
    return {"datasets":n,"rows":rows,"last_upload":last["created_at"] if last else None}

@app.get("/api/uploads")
def uploads(request:Request):
    session(request); c=db(); return [dict(x) for x in c.execute("select * from uploads order by id desc limit 50").fetchall()]

@app.post("/api/upload")
async def upload(request:Request,file:UploadFile=File(...)):
    s=session(request); ext=Path(file.filename or "").suffix.lower()
    if ext not in {".csv",".xlsx",".json"}: raise HTTPException(400,"Formato permitido: CSV, XLSX o JSON")
    raw=await file.read()
    if len(raw)>25*1024*1024: raise HTTPException(413,"Máximo 25 MB")
    safe=f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{Path(file.filename).name}"; (UPLOADS/safe).write_bytes(raw)
    try:
        if ext==".csv": frame=pd.read_csv(io.BytesIO(raw))
        elif ext==".xlsx": frame=pd.read_excel(io.BytesIO(raw))
        else: frame=pd.read_json(io.BytesIO(raw))
    except Exception as e: (UPLOADS/safe).unlink(missing_ok=True); raise HTTPException(400,f"No se pudo interpretar el archivo: {e}")
    now=datetime.now(timezone.utc).isoformat(); c=db()
    cur=c.execute("insert into uploads(filename,kind,size,rows,columns,created_at,user) values(?,?,?,?,?,?,?)",(safe,ext[1:],len(raw),len(frame),len(frame.columns),now,s["user"])); c.commit()
    item={"id":cur.lastrowid,"filename":safe,"kind":ext[1:],"size":len(raw),"rows":len(frame),"columns":len(frame.columns),"created_at":now,"user":s["user"]}
    await broadcast("upload",item); return item

@app.post("/api/knowledge/upload")
async def knowledge_upload(request:Request,file:UploadFile=File(...)):
    s=session(request); ext=Path(file.filename or "").suffix.lower()
    if ext not in {".pdf",".txt",".md",".docx"}: raise HTTPException(400,"Formato permitido: PDF, TXT, MD o DOCX")
    raw=await file.read()
    if len(raw)>25*1024*1024: raise HTTPException(413,"Máximo 25 MB")
    name=f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{Path(file.filename).name}"; (KNOWLEDGE/name).write_bytes(raw)
    item={"filename":name,"size":len(raw),"user":s["user"]}; await broadcast("knowledge",item); return item

@app.get("/api/forecast/{upload_id}")
def forecast(upload_id:int,request:Request):
    session(request); c=db(); row=c.execute("select * from uploads where id=?",(upload_id,)).fetchone()
    if not row: raise HTTPException(404,"Dataset no encontrado")
    p=UPLOADS/row["filename"]
    try:
        frame=pd.read_csv(p) if row["kind"]=="csv" else pd.read_excel(p) if row["kind"]=="xlsx" else pd.read_json(p)
        nums=frame.select_dtypes(include="number")
        if nums.empty: raise HTTPException(400,"El dataset no contiene columnas numéricas")
        col=nums.columns[0]; vals=nums[col].dropna().tail(20).tolist()
        if len(vals)<2: raise HTTPException(400,"Datos insuficientes")
        slope=(vals[-1]-vals[0])/(len(vals)-1); pred=[round(vals[-1]+slope*i,4) for i in range(1,6)]
        return {"column":str(col),"method":"linear-trend-baseline","forecast":pred}
    except HTTPException: raise
    except Exception as e: raise HTTPException(400,str(e))

@app.websocket("/ws")
async def ws_endpoint(ws:WebSocket):
    origin=ws.headers.get("origin")
    if origin!=ORIGIN: await ws.close(code=1008); return
    await ws.accept(); sockets.add(ws)
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect: sockets.discard(ws)
