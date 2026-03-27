# lidar_project
융합_로보테크 AI 자율주행 로봇 개발자 과정 실습
가짜 라이다 센서 데이터를 만들어, 로봇이 장애물을 피해 움직이는 걸 시뮬레이션하는 프로젝트

## 프로젝트 구조 및 한계

### 구현된 것
```
가짜 Lidar 데이터 생성 (랜덤 패턴)
       v
ROS2 /scan 토픽으로 2초마다 발행
       v
roslibpy로 수신 후 주행 방향 결정
       v
turtlesim 거북이 이동 명령 발행
       v
MySQL에 데이터 저장 및 DataFrame/NumPy 파싱
```

### 한계
```
- turtlesim 화면 경계 감지 없음 -> 거북이가 밖으로 나감
- Lidar 데이터가 거북이 실제 위치와 무관한 랜덤 패턴
- 실제 장애물 회피 성능 없음
```

이 프로젝트의 목적은 장애물 회피 성능 구현이 아니라,
Lidar 데이터 생성부터 ROS2 토픽 발행, 수신, 주행 결정, DB 저장, 파싱까지
전체 파이프라인을 구축하는 것에 있음

---

## 진행 현황
| 단계 | 위치 | 내용 | 상태 |
|------|------|------|------|
| 1단계 | WSL | LiDAR 모의 데이터 생성 & /scan 토픽 발행 | 완료 |
| 2단계 | Windows | /scan 토픽 수신 & 주행 방향 결정 | 완료 |
| 3단계 | Windows | turtlesim에 주행 명령 발행 | 완료 |
| 4단계 | Windows | MySQL에 데이터 저장 | 완료 |
| 5단계 | Windows | MySQL 데이터 파싱 & CSV 출력 | 완료 |

---

## 1단계 -- LiDAR Publisher (WSL)

### 파일 위치
```
ros2_ws/src/lidar_publisher/lidar_publisher/lidar_publisher_node.py
```

### 동작 원리

2초마다 아래 3가지 패턴 중 하나를 랜덤으로 골라 `/scan` 토픽으로 발행함
```
front_wall : 앞(0도)에 벽이 있는 상황
left_wall  : 왼쪽(90도)에 벽이 있는 상황
right_wall : 오른쪽(270도)에 벽이 있는 상황
```

각도 기준:
```
앞 (0도), 왼쪽(90도), 오른쪽(270도), 뒤 (180도)
```

### 데이터 구조

LaserScan 메시지는 360개의 거리값 리스트(1도당 1개)
```
ranges = [3.5, 3.5, ..., 0.4, 0.4, ..., 3.5]
          0도  1도       장애물 구간       359도

- 3.5m : 장애물 없음 (최대 측정 거리)
- 0.4m : 장애물 있음 (벽까지 40cm)
```

### 주요 설정값

| 상수 | 값 | 의미 |
|------|----|------|
| `RANGE_MIN` | 0.12m | 최소 측정 거리 (12cm) |
| `RANGE_MAX` | 3.5m | 최대 측정 거리 (장애물 없음 기준) |
| `NUM_POINTS` | 360 | 1도마다 1개, 총 360개 데이터 |
| `WALL_DIST` | 0.4m | 가짜 벽까지의 거리 (40cm) |
| `PUBLISH_INTERVAL` | 2.0초 | 데이터 발행 주기 |

### 코드 구조 요약
```
create_empty_ranges()          전방향 3.5m로 채운 빈 데이터 생성
make_the_wall()                특정 방향에 0.4m 장애물 심기
generate_scan_ranges()         패턴 이름에 따라 위 두 함수 조합
LidarPublisher.publish_scan()  2초마다 자동 실행, LaserScan 메시지 완성 후 발행
```

### 실행 방법
```bash
cd ~/lidar_project/ros2_ws
source install/setup.bash
ros2 run lidar_publisher lidar_publisher_node
```

### 토픽 확인 방법
```bash
source ~/lidar_project/ros2_ws/install/setup.bash
ros2 topic echo /scan
```

---

## 2단계 -- Remote PC Subscriber (Windows)

### 파일 위치
```
remote_pc.py
```

### 동작 원리
roslibpy를 통해 rosbridge_server에 WebSocket으로 접속하여 `/scan` 토픽을 수신하고 주행 액션을 결정함
```
go_forward : 전방 거리가 안전거리(0.5m) 이상인 경우
turn_left  : 전방에 장애물이 있고 왼쪽이 더 넓은 경우
turn_right : 전방에 장애물이 있고 오른쪽이 더 넓은 경우
```

### 주행 결정 기준
```
전방   : ranges[350:360] + ranges[0:10] 평균
왼쪽   : ranges[80:100] 평균
오른쪽 : ranges[260:280] 평균
안전거리 : 0.5m
```

### 주요 설정값
| 상수 | 값 | 의미 |
|------|----|------|
| `HOST` | 192.168.0.204 | ROS PC의 Windows IP |
| `PORT` | 9090 | rosbridge WebSocket 포트 |
| `SAFE_DIST` | 0.5m | 장애물 판단 기준 거리 |

### 사전 준비 (ROS PC WSL에서 먼저 실행)
```bash
# 터미널 1 - Publisher 실행
source /opt/ros/humble/setup.bash
source ~/lidar_project/ros2_ws/install/setup.bash
ros2 run lidar_publisher lidar_publisher_node
# 터미널 2 - rosbridge 실행
source /opt/ros/humble/setup.bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

### 실행 방법
```bash
python remote_pc.py
```

---

## 3단계 -- Turtlesim 주행 명령 발행 (Windows)

### 파일 위치
```
turtle_driver.py
```

### 동작 원리
결정된 액션을 기반으로 `/turtle1/cmd_vel` 토픽에 Twist 메시지를 발행하여 turtlesim 거북이를 실제로 움직임
```
go_forward : linear.x = 1.0   (직진)
turn_left  : angular.z = 1.0  (좌회전)
turn_right : angular.z = -1.0 (우회전)
```

### 사전 준비 (ROS PC WSL에서 먼저 실행)
```bash
# 터미널 1 - Publisher 실행
source /opt/ros/humble/setup.bash
source ~/lidar_project/ros2_ws/install/setup.bash
ros2 run lidar_publisher lidar_publisher_node
# 터미널 2 - rosbridge 실행
source /opt/ros/humble/setup.bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
# 터미널 3 - turtlesim 실행
source /opt/ros/humble/setup.bash
ros2 run turtlesim turtlesim_node
```

### 실행 방법
```bash
python turtle_driver.py
```

---

## 4단계 -- MySQL 데이터 저장 (Windows)

### 파일 위치
```
turtle_driver.py (3단계 코드에 통합)
```

### 테이블 스키마
```sql
CREATE DATABASE rosdb;
USE rosdb;

CREATE TABLE lidardata (
    id      INT           AUTO_INCREMENT PRIMARY KEY,
    ranges  JSON          NOT NULL,
    `when`  DATETIME      NOT NULL,
    action  VARCHAR(20)   NOT NULL
);
```

### 동작 원리
/scan 토픽 수신 시마다 ranges[], 수신 시각, 주행 액션을 lidardata 테이블에 INSERT함

### 주요 설정값
| 상수 | 값 | 의미 |
|------|----|------|
| `host` | localhost | MySQL 서버 주소 |
| `user` | root | MySQL 사용자 |
| `database` | rosdb | 사용할 스키마 |

---

## 5단계 -- MySQL 데이터 파싱 & CSV 출력 (Windows)

### 파일 위치
```
parse_lidar.py
```

### 동작 원리
MySQL lidardata 테이블에서 데이터를 조회하여 JSON 타입의 ranges[]를 360개 개별 컬럼으로 변환한 뒤 DataFrame 및 NumPy Array로 출력하고 CSV로 저장함

### 최종 데이터 구조
```
range_0, range_1, ..., range_359, action
  (각도별 거리값 360개)           (주행 액션)
총 361개 컬럼
```

### 출력 결과
```
- DataFrame   : 375행 x 361컬럼
- NumPy Array : shape (375, 361)
- CSV 파일    : output.csv
```

### 실행 방법
```bash
python parse_lidar.py
```
