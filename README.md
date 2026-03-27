# 🚗 LiDAR 기반 모의 자율주행 시스템 (ROS)

## 📌 프로젝트 개요
가짜 LiDAR 센서 데이터를 생성하여 ROS2 토픽으로 발행하고,  
이를 수신하여 로봇(거북이)이 장애물을 회피하며 움직이도록 하는  
모의 자율주행 시뮬레이션 프로젝트입니다.

---

## ⚙️ 시스템 구조


LiDAR (Mock Data)
↓
ROS2 /scan Topic
↓
rosbridge (WebSocket)
↓
Python (roslibpy)
↓
주행 방향 결정 (Rule 기반)
↓
turtlesim 이동 (/cmd_vel)
↓
MySQL 저장 → DataFrame/NumPy 변환

---
## 🚀 주요 기능

- 360도 LiDAR 데이터 생성 (랜덤 패턴)
- ROS2 `/scan` 토픽 2초 주기 발행
- roslibpy로 원격 수신
- 거리 기반 주행 판단 (직진 / 좌회전 / 우회전)
- turtlesim 실시간 제어
- MySQL 데이터 저장
- JSON → 360개 컬럼 데이터셋 변환
---

## 🧠 주행 알고리즘

    python
if front_dist < safe_dist:
    action = "turn_left" if left_dist > right_dist else "turn_right"
else:
    action = "go_forward"


---

🗄️ 데이터 구조
컬럼	설명
id	    고유 ID
ranges	360도 거리 데이터 (JSON)
when	저장 시간
action	주행 결과

👉 변환 후 데이터:

range_0 ~ range_359 + action = 총 361개 컬럼

---

▶️ 실행 방법

1️⃣ LiDAR Publisher (WSL)

ros2 run lidar_publisher lidar_publisher_node

2️⃣ rosbridge 실행

ros2 launch rosbridge_server rosbridge_websocket_launch.xml

3️⃣ turtlesim 실행

ros2 run turtlesim turtlesim_node

4️⃣ Python 실행 (Windows)

python turtle_driver.py


---

📊 진행 현황
단계	     내용	                상태
1	LiDAR 데이터 생성 & /scan 발행	✅/n
2	토픽 수신 & 주행 판단	✅/n
3	turtlesim 제어	✅/n
4	MySQL 데이터 저장	✅/n
5	데이터 파싱 & CSV 생성	✅/n

---
⚠️ 한계
turtlesim 경계 감지 없음
LiDAR 데이터가 실제 위치와 무관한 랜덤 패턴
실제 장애물 회피 성능 없음

👉 프로젝트 목적:
센서 → ROS → 제어 → DB → 분석까지 전체 흐름 구현

👨‍💻 개발자

김아영 (Computer Science)
