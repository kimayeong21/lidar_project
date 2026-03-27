import roslibpy
import numpy as np
import pymysql
from datetime import datetime
import json

# ROS 연결
client = roslibpy.Ros(host='localhost', port=9090)
client.run()

print("Connected:", client.is_connected)

# DB 연결
db = pymysql.connect(
    host="localhost",
    user="ayeong",
    password="1234",
    database="lidar_db"
)

cursor = db.cursor()

def process_scan(message):
    ranges = np.array(message['ranges'])

    front = np.r_[ranges[350:360], ranges[0:10]]
    left  = ranges[80:100]
    right = ranges[260:280]

    front_dist = np.mean(front)
    left_dist  = np.mean(left)
    right_dist = np.mean(right)

    safe_dist = 0.5

    if front_dist < safe_dist:
        action = "turn_left" if left_dist > right_dist else "turn_right"
    else:
        action = "go_forward"

    print("ACTION:", action)

    # DB 저장
    sql = """
    INSERT INTO lidardata (ranges, action, created_at)
    VALUES (%s, %s, %s)
    """

    cursor.execute(sql, (
        json.dumps(ranges.tolist()),
        action,
        datetime.now()
    ))

    db.commit()

    print("✅ DB 저장 완료")


listener = roslibpy.Topic(client, '/scan', 'sensor_msgs/LaserScan')
listener.subscribe(process_scan)

while True:
    pass
