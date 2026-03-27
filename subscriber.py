import roslibpy
import numpy as np

# 🔥 ROS 연결
client = roslibpy.Ros(host='localhost', port=9090)
client.run()

print("Connected:", client.is_connected)

# 🔥 거북이 제어 퍼블리셔
cmd_pub = roslibpy.Topic(client, '/turtle1/cmd_vel', 'geometry_msgs/Twist')

def process_scan(message):
    ranges = np.array(message['ranges'])

    # 🔥 방향 나누기
    front = np.r_[ranges[350:360], ranges[0:10]]
    left  = ranges[80:100]
    right = ranges[260:280]

    front_dist = np.mean(front)
    left_dist  = np.mean(left)
    right_dist = np.mean(right)

    safe_dist = 0.5

    # 🔥 기본 rule 기반 판단
    if front_dist < safe_dist:
        action = "turn_left" if left_dist > right_dist else "turn_right"
    else:
        action = "go_forward"

    print("ACTION:", action)

    # 🔥 거북이 움직임 설정
    twist = {
        'linear': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        'angular': {'x': 0.0, 'y': 0.0, 'z': 0.0}
    }

    if action == "go_forward":
        twist['linear']['x'] = 2.0
    elif action == "turn_left":
        twist['angular']['z'] = 2.0
    elif action == "turn_right":
        twist['angular']['z'] = -2.0

    # 🔥 publish
    cmd_pub.publish(roslibpy.Message(twist))


# 🔥 LiDAR 구독
listener = roslibpy.Topic(client, '/scan', 'sensor_msgs/LaserScan')
listener.subscribe(process_scan)

while True:
    pass