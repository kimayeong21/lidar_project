# 🚗 LiDAR 기반 모의 자율주행 시스템 (ROS)

## 📌 프로젝트 개요
본 프로젝트는 LiDAR 센서 데이터를 활용하여 주변 환경을 인식하고,  
자율적으로 주행 방향을 결정하는 모의 자율주행 시스템입니다.  

ROS2 환경에서 센서 데이터를 생성하고 Python을 통해 분석하여  
거북이(turtlesim)의 움직임을 제어하도록 구현하였습니다.

---

## 🎯 개발 목적
- 센서 데이터를 활용한 자율주행 구조 이해
- ROS2 기반 데이터 흐름 학습
- 거리 기반 주행 알고리즘 구현
- 데이터 저장 및 분석 기반 구축

---

## 🛠️ 기술 스택

- ROS2 (Jazzy)
- Python
- roslibpy
- MySQL
- NumPy / Pandas

---

## ⚙️ 시스템 구조
LiDAR (Mock Data)
↓
/scan Topic
↓
rosbridge
↓
Python Subscriber
↓
주행 알고리즘 (Rule 기반)
↓
turtle1/cmd_vel
↓
Turtlesim 이동
↓
MySQL 저장


---

## 🚀 주요 기능

### 1️⃣ LiDAR 데이터 생성
- 360도 거리 데이터 생성
- 장애물 패턴 (전방 / 좌 / 우) 구성

### 2️⃣ 데이터 수신
- roslibpy를 이용한 ROS 통신
- /scan 토픽 실시간 구독

### 3️⃣ 주행 알고리즘
- 전방, 좌측, 우측 거리 분석
- 안전거리 기준 판단

```python
if front_dist < safe_dist:
    action = "turn_left" if left_dist > right_dist else "turn_right"
else:
    action = "go_forward"


---

## 🚀 주요 기능

### 1️⃣ LiDAR 데이터 생성
- 360도 거리 데이터 생성
- 장애물 패턴 (전방 / 좌 / 우) 구성

### 2️⃣ 데이터 수신
- roslibpy를 이용한 ROS 통신
- /scan 토픽 실시간 구독

### 3️⃣ 주행 알고리즘
- 전방, 좌측, 우측 거리 분석
- 안전거리 기준 판단

```python
if front_dist < safe_dist:
    action = "turn_left" if left_dist > right_dist else "turn_right"
else:
    action = "go_forward"

🗄️ 데이터 구조
컬럼명	설명
id	고유 ID
ranges	360도 거리 데이터 (JSON)
action	주행 행동
created_at	저장 시간

📊 데이터셋 변환
JSON 데이터를 360개 컬럼으로 변환
머신러닝 학습 가능한 형태로 구성
(데이터 수, 361 컬럼)
→ 360개 거리값 + 1개 action

▶️ 실행 방법
1. LiDAR 데이터 생성
ros2 run lidar_mock lidar_publisher
2. rosbridge 실행
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
3. turtlesim 실행
ros2 run turtlesim turtlesim_node
4. Python 실행
python subscriber.py

🎥 실행 결과
LiDAR 데이터를 기반으로 거북이가 자율적으로 이동
장애물 회피 동작 수행
실시간 데이터 저장

💡 기대 효과
자율주행 시스템의 기본 구조 이해
ROS 기반 센서 처리 경험
데이터 기반 확장 가능 (AI 적용 가능)

📌 향후 개선 방향
머신러닝 기반 주행 판단 적용
다양한 센서 데이터 통합
실제 하드웨어 적용 (Arduino / ROS 연동)

👨‍💻 개발자
김아영 (Computer Science)
