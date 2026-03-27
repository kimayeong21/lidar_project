import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import random
import math


class LidarPublisher(Node):

    def __init__(self):
        super().__init__('lidar_publisher')

        self.publisher_ = self.create_publisher(LaserScan, '/scan', 10)
        self.timer = self.create_timer(2.0, self.publish_scan)

        print("🔥 lidar_publisher 시작됨")

    def publish_scan(self):
        msg = LaserScan()

        msg.angle_min = 0.0
        msg.angle_max = 2 * math.pi
        msg.angle_increment = math.radians(1)

        msg.range_min = 0.12
        msg.range_max = 3.5

        ranges = [3.5] * 360

        pattern = random.choice(["front", "left", "right"])

        if pattern == "front":
            for i in list(range(350, 360)) + list(range(0, 10)):
                ranges[i] = 0.4

        elif pattern == "left":
            for i in range(80, 100):
                ranges[i] = 0.4

        elif pattern == "right":
            for i in range(260, 280):
                ranges[i] = 0.4

        msg.ranges = ranges

        self.publisher_.publish(msg)
        self.get_logger().info(f"Published: {pattern}")


def main(args=None):
    rclpy.init(args=args)
    node = LidarPublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
