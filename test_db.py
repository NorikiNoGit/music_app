from dotenv import load_dotenv
import psycopg2
import os

load_dotenv()  # .envファイルから環境変数を読み込む

conn = psycopg2.connect(
        dbname="musicdb",
        user="noriki",
        password=os.environ.get("DB_PASSWORD"),
        #host=os.environ.get("DB_HOST"),
        # host="192.168.11.11",  # リモートならIP指定
        host="localhost",  # ローカルならlocalhost
        port=5432
    )
cursor = conn.cursor()
cursor.execute("SELECT * FROM music ORDER BY created_at DESC")
rows = cursor.fetchall()
conn.close()

# データベースの内容を表示
for row in rows:
    print(row)
