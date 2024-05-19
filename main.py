import json
from json.decoder import JSONDecodeError
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import Response

from fastapi.staticfiles import StaticFiles
from jinja2 import Template
import redis
from fastapi import FastAPI, Form
from collections import defaultdict
import os
app = FastAPI()

# Static files (CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Redis connection
redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")
print("--"*10)
print("redis_host", redis_host)
print("redis_port", redis_port)
print("--"*10)
r = redis.Redis(host=redis_host, port=redis_port, db=0)

# Template rendering function
def render_template(template_name, **context):
    with open(f'templates/{template_name}', 'r') as file:
        template = Template(file.read())
    return HTMLResponse(content=template.render(context))

def group_keys(keys):
    grouped = defaultdict(list)
    for key in keys:
        decoded_key = key.decode('utf-8')
        parts = decoded_key.split(':', 1)
        if len(parts) == 2:
            grouped[parts[0]].append((parts[1], r.get(key).decode('utf-8')))
        else:
            grouped[decoded_key].append(('', r.get(key).decode('utf-8')))
    return grouped


@app.post("/search")
async def search(pattern: str = Form(...)):
    keys = r.keys(f'*{pattern}*')
    grouped_keys = group_keys(keys)
    for folder, items in grouped_keys.items():
        for i, (subkey, value) in enumerate(items):
            try:
                parsed_value = json.loads(value)
                grouped_keys[folder][i] = (subkey, parsed_value)
            except json.JSONDecodeError:
                pass
    return render_template('index.html', grouped_keys=grouped_keys, all_open=True, search_pattern=pattern)


@app.get("/")
async def index():
    keys = r.keys('*')
    grouped_keys = group_keys(keys)
    return render_template('index.html', grouped_keys=grouped_keys, all_open=True, search_pattern='')

    
    
@app.get("/value/{key_path}", response_class=HTMLResponse)
async def get_value(key_path: str):
    # Redis에서 지정된 키의 값을 조회합니다.
    value = r.get(key_path)
    if value:
        try:
            parsed_value = json.loads(value)
            pretty_value = json.dumps(parsed_value, indent=4)
        except JSONDecodeError:
            pretty_value = value.decode('utf-8')
    else:
        pretty_value = "Key does not exist."

    # 해당하는 key에 대한 value를 HTML 형식으로 반환합니다.
    return Response(content=pretty_value, media_type="text/html")
