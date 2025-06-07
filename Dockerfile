FROM python:3.12-slim

# 必要なシステムツール追加（ffmpeg含む）
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

WORKDIR /MUSIC_APP
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# CMD ["python", "app/app.py"]
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app.app:app", "--access-logfile", "-"]