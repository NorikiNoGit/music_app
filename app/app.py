from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from yt_dlp import YoutubeDL
from datetime import datetime
import sqlite3
import re

app = Flask(__name__)

# 設定
MUSIC_DIR = "/musicshare"  # 実際のmp3保存場所（Samba共有）
DB_PATH = "music.db"           # SQLiteファイル

def safe_filename(name):
    # ファイル名に使えない文字をアンダースコアに置換
    return re.sub(r'[<>:"/\\|?*\n\r\t]', '_', name).strip()

# ======================
# 音楽一覧再生ページ
# ======================
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form.get("url")
        try:
            download_audio(url)
        except Exception as e:
            return f"<p>❌ エラーが発生しました: {str(e)}</p>"
        return redirect(url_for("index"))

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filepath, title, artist FROM music ORDER BY created_at DESC")
    songs = cursor.fetchall()
    conn.close()
    return render_template("index.html", songs=songs)

# ======================
# mp3ファイルの提供
# ======================
@app.route("/music/<filename>")
def serve_music(filename):
    return send_from_directory(MUSIC_DIR, filename)

# ======================
# YouTube → mp3 変換 & DB登録
# ======================
def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(MUSIC_DIR, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        raw_title = info.get("title", "Unknown Title")
        title = safe_filename(raw_title)
        artist = info.get("uploader", "Unknown Artist")
        duration = info.get("duration", 0)

        # ファイルパスを正確に取得する
        downloaded_filename = ydl.prepare_filename(info)
        mp3_filepath = os.path.splitext(downloaded_filename)[0] + ".mp3"
        filename_only = os.path.basename(mp3_filepath)
        
        # 確実にファイルが存在するかチェック
        if not os.path.exists(mp3_filepath):
            raise FileNotFoundError(f"ファイルが見つかりません: {mp3_filepath}")

        filesize = os.path.getsize(mp3_filepath)
        created_at = datetime.now().isoformat()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO music (filepath, title, artist, duration, filesize, created_at, source_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (filename_only, raw_title, artist, duration, filesize, created_at, url))
        conn.commit()
        conn.close()



# ======================
# データベース確認
# ======================
@app.route("/debug/db")
def debug_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM music ORDER BY created_at DESC")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    return render_template("debug_db.html", rows=rows, columns=columns)

@app.route("/debug/edit/<int:music_id>", methods=["GET", "POST"])
def edit_entry(music_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form.get("title")
        artist = request.form.get("artist")
        tags = request.form.get("tags")
        genre_ai = request.form.get("genre_ai")

        cursor.execute("""
            UPDATE music
            SET title = ?, artist = ?, tags = ?, genre_ai = ?
            WHERE id = ?
        """, (title, artist, tags, genre_ai, music_id))

        conn.commit()
        conn.close()
        return redirect(url_for("debug_db"))
    
    # GET: 現在の値を取得して表示
    cursor.execute("SELECT title, artist, tags, genre_ai FROM music WHERE id = ?", (music_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        return render_template("edit_entry.html", music_id=music_id, title=result[0], artist=result[1], tags=result[2], genre_ai=result[3])
    else:
        return "❌ レコードが見つかりませんでした", 404

@app.route("/debug/delete/<int:music_id>", methods=["POST"])
def delete_entry(music_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM music WHERE id = ?", (music_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("debug_db"))


# ======================
# アプリ起動
# ======================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
