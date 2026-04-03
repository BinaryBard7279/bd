from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.admin import setup_admin

app = FastAPI(title="API")

setup_admin(app)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    Всё работает <br><br>
    <a href='/admin'>/admin</a> для управления базой данных.
    """