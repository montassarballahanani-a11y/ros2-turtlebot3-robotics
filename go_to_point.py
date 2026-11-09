import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import math


class GoToPoint(Node):

    def __init__(self):
        super().__init__('go_to_point')

        self.declare_parameter('goal_x', 1.0)
        self.declare_parameter('goal_y', 1.0)

        self.target_x = self.get_parameter('goal_x').value
        self.target_y = self.get_parameter('goal_y').value
        self.publisher = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.get_logger().info(
            f'Goal: x={self.target_x}, y={self.target_y}'
        )

    def odom_callback(self, msg):

        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

        q = msg.pose.pose.orientation

        siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
        cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)

        self.yaw = math.atan2(siny_cosp, cosy_cosp)
        dx = self.target_x - self.x
        dy = self.target_y - self.y

        distance = math.sqrt(dx**2 + dy**2)

        target_angle = math.atan2(dy, dx)

        angle_error = target_angle - self.yaw
        angle_error = math.atan2(
            math.sin(angle_error),
            math.cos(angle_error)
        )

        cmd = Twist()

        if distance > 0.1:

            if abs(angle_error) > 0.1:
                cmd.linear.x = 0.0
                cmd.angular.z = 0.5 * angle_error

            else:
                cmd.linear.x = 0.15
                cmd.angular.z = 0.0

        else:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            self.get_logger().info('Destination atteinte !')

        self.publisher.publish(cmd)
def main(args=None):

    rclpy.init(args=args)

    node = GoToPoint()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
