# LiDAR 기반 모의 자율주행 시스템

ROS2 환경에서 가상의 LiDAR 센서 데이터를 생성하고, 수신한 거리 데이터를 바탕으로 주행 방향을 판단하는 모의 자율주행 프로젝트입니다. `/scan` 토픽으로 발행되는 360도 거리 데이터를 Python에서 구독한 뒤, 전방·좌측·우측 거리 값을 비교하여 직진, 좌회전, 우회전 동작을 결정합니다.

이 프로젝트는 센서 데이터 생성, ROS 토픽 통신, 주행 판단 로직, MySQL 저장, CSV 데이터셋 변환까지 하나의 흐름으로 구성되어 있습니다.

## 프로젝트 개요

LiDAR 센서가 주변 장애물과의 거리를 측정한다는 상황을 가정하고, ROS2 Publisher가 360개의 거리 값을 생성합니다. Python 구독 프로그램은 이 데이터를 받아 전방 장애물 여부를 판단하고, 안전 거리에 따라 이동 방향을 선택합니다.

또한 수신한 LiDAR 데이터를 MySQL에 저장하고, 저장된 데이터를 다시 CSV 형식의 학습용 데이터셋으로 변환할 수 있도록 구성했습니다. 실제 센서가 없어도 LiDAR 데이터 처리 흐름을 실습할 수 있다는 점에 초점을 둔 프로젝트입니다.

## 주요 구현 내용

- ROS2 기반 Mock LiDAR Publisher 구현
- `/scan` 토픽을 통한 `sensor_msgs/LaserScan` 데이터 발행
- `rosbridge`와 `roslibpy`를 이용한 Python 기반 토픽 구독
- 전방, 좌측, 우측 영역의 평균 거리 계산
- 안전 거리 기준의 Rule 기반 주행 방향 판단
- 판단 결과를 `geometry_msgs/Twist` 형태로 `/turtle1/cmd_vel`에 발행
- LiDAR 원본 거리 데이터와 주행 판단 결과를 MySQL에 저장
- MySQL에 저장된 JSON 형태의 거리 데이터를 CSV 데이터셋으로 변환

## 시스템 흐름

```text
Mock LiDAR Publisher
        |
        v
ROS2 /scan Topic
        |
        v
rosbridge WebSocket
        |
        v
Python Subscriber
        |
        +--> 주행 방향 판단
        |
        +--> turtlesim 제어
        |
        +--> MySQL 저장
        |
        v
CSV 데이터셋 생성
```

## 주행 판단 로직

LiDAR 데이터는 0도부터 359도까지 총 360개의 거리 값으로 구성됩니다. 이 프로젝트에서는 전방, 좌측, 우측 구간을 나누어 평균 거리를 계산합니다.

```python
front = np.r_[ranges[350:360], ranges[0:10]]
left = ranges[80:100]
right = ranges[260:280]
```

전방 평균 거리가 안전 거리보다 짧으면 장애물이 있다고 판단합니다. 이때 좌측과 우측 거리 중 더 넓은 방향으로 회전하고, 전방이 안전하면 직진합니다.

```python
if front_dist < safe_dist:
    action = "turn_left" if left_dist > right_dist else "turn_right"
else:
    action = "go_forward"
```

## 데이터 저장 구조

MySQL에는 LiDAR 거리 데이터와 판단 결과가 함께 저장됩니다. 거리 데이터는 360개의 값을 JSON 문자열 형태로 저장하고, 이후 데이터셋 변환 과정에서 각 각도별 컬럼으로 펼쳐집니다.

저장 데이터 예시는 다음과 같습니다.

```text
ranges      360도 LiDAR 거리 데이터(JSON)
action      go_forward / turn_left / turn_right
created_at  데이터 저장 시간
```

CSV 변환 결과는 `angle_0`부터 `angle_359`까지의 거리 컬럼과 `action` 컬럼으로 구성됩니다.

## 프로젝트 구조

```text
lidar_project
├── README.md
├── subscriber.py
├── subscriber_db.py
├── dataset_builder.py
├── lidar_dataset.csv
└── src
    └── lidar_mock
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource
        │   └── lidar_mock
        ├── lidar_mock
        │   ├── __init__.py
        │   └── lidar_publisher.py
        └── test
            ├── test_copyright.py
            ├── test_flake8.py
            └── test_pep257.py
```

## 파일 설명

`src/lidar_mock/lidar_mock/lidar_publisher.py`는 ROS2 환경에서 가상의 LiDAR 데이터를 생성해 `/scan` 토픽으로 발행합니다. 전방, 좌측, 우측 중 하나의 위치에 장애물이 있는 상황을 무작위로 만들고, 2초 간격으로 LaserScan 메시지를 전송합니다.

`subscriber.py`는 `rosbridge`를 통해 `/scan` 데이터를 구독하고, 거리 기반 주행 판단을 수행합니다. 판단 결과에 따라 turtlesim의 `/turtle1/cmd_vel` 토픽으로 이동 명령을 발행합니다.

`subscriber_db.py`는 LiDAR 데이터를 구독한 뒤 주행 판단 결과와 함께 MySQL 데이터베이스에 저장합니다. 센서 데이터 수집과 판단 결과 기록을 함께 확인할 때 사용합니다.

`dataset_builder.py`는 MySQL에 저장된 LiDAR 데이터를 불러와 CSV 데이터셋으로 변환합니다. JSON 형태의 360도 거리 데이터를 각도별 컬럼으로 분리하고, 마지막에 `action` 컬럼을 추가합니다.

`lidar_dataset.csv`는 변환된 LiDAR 데이터셋 예시 파일입니다.

## 사용 기술

- Python
- ROS2
- rclpy
- roslibpy
- NumPy
- pandas
- PyMySQL
- MySQL
- rosbridge
- turtlesim

## 실행 방법

ROS2 워크스페이스에서 패키지를 빌드합니다.

```bash
colcon build
source install/setup.bash
```

Mock LiDAR Publisher를 실행합니다.

```bash
ros2 run lidar_mock lidar_publisher
```

rosbridge WebSocket 서버를 실행합니다.

```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

turtlesim을 실행합니다.

```bash
ros2 run turtlesim turtlesim_node
```

Python 구독 및 제어 프로그램을 실행합니다.

```bash
python subscriber.py
```

MySQL 저장 기능을 확인하려면 데이터베이스와 테이블을 준비한 뒤 다음 파일을 실행합니다.

```bash
python subscriber_db.py
```

저장된 데이터를 CSV로 변환하려면 다음 파일을 실행합니다.

```bash
python dataset_builder.py
```

## MySQL 테이블 예시

```sql
CREATE DATABASE lidar_db;

USE lidar_db;

CREATE TABLE lidardata (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ranges JSON NOT NULL,
    action VARCHAR(30) NOT NULL,
    created_at DATETIME NOT NULL
);
```

`subscriber_db.py`와 `dataset_builder.py`의 MySQL 접속 정보는 실행 환경에 맞게 수정해야 합니다.

## 프로젝트 특징

이 프로젝트는 실제 LiDAR 센서 없이도 자율주행 데이터 처리 흐름을 단계별로 확인할 수 있도록 구성했습니다. 센서 메시지 생성부터 주행 판단, 로봇 시뮬레이션 제어, 데이터 저장과 전처리까지 이어지는 구조라 ROS와 Python 기반 로봇 소프트웨어의 기본 흐름을 익히기에 적합합니다.

## 개선 방향

- 실제 LiDAR 센서 데이터 연동
- 장애물 회피 알고리즘 고도화
- 주행 판단 기준을 Rule 기반에서 학습 기반 모델로 확장
- 저장 데이터 시각화 기능 추가
- 환경 설정 값을 별도 설정 파일로 분리

## 개발자

김아영
