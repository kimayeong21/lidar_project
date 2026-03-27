import pymysql
import pandas as pd
import json

# 🔥 DB 연결
db = pymysql.connect(
    host="localhost",
    user="ayeong",
    password="1234",
    database="lidar_db"
)

# 🔥 데이터 가져오기
query = "SELECT ranges, action FROM lidardata"
df = pd.read_sql(query, db)

print("원본 데이터 개수:", len(df))

# 🔥 JSON → 리스트 변환
df['ranges'] = df['ranges'].apply(json.loads)

# 🔥 리스트 → 360 컬럼
ranges_df = pd.DataFrame(df['ranges'].tolist())

# 🔥 컬럼 이름 설정 (0~359)
ranges_df.columns = [f"angle_{i}" for i in range(360)]

# 🔥 action 붙이기
ranges_df['action'] = df['action']

print("변환된 데이터 형태:", ranges_df.shape)
print(ranges_df.head())

# 🔥 CSV 저장 (선택)
ranges_df.to_csv("lidar_dataset.csv", index=False)

print("✅ 데이터셋 생성 완료")
