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

