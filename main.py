import shutil
import os
from fastapi import FastAPI, UploadFile, File, Form, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base, Session

# --- CONFIGURATION ---
app = FastAPI()

# Create folders for videos if they don't exist
os.makedirs("static/videos", exist_ok=True)

# Mount the static folder so HTML can see CSS and Videos
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- DATABASE (SQLite for simplicity, scalable to Azure SQL) ---
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# Database Tables


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)


class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    filename = Column(String)


# Create DB
Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ROUTES ---


@app.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    # Auto-register user if they don't exist (Keeps code simple!)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        new_user = User(username=username, password=password)
        db.add(new_user)
        db.commit()
    return RedirectResponse(url="/feed", status_code=303)


@app.get("/feed", response_class=HTMLResponse)
async def feed(request: Request, db: Session = Depends(get_db)):
    videos = db.query(Video).all()
    return templates.TemplateResponse("feed.html", {"request": request, "videos": videos})


@app.post("/upload")
async def upload(title: str = Form(...), file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save video to folder
    file_location = f"static/videos/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save info to DB
    new_video = Video(title=title, filename=file.filename)
    db.add(new_video)
    db.commit()
    return RedirectResponse(url="/feed", status_code=303)


templates = Jinja2Templates(directory="templates")
