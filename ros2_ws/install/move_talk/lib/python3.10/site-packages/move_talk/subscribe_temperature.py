import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class SubscribeTemperature(Node):
    def __init__(self):
        super().__init__('subscribe_temperature')
        
        self.subscription = self.create_subscription(
            String,
            'temp_topic',
            self.listener_callback,
            10
        )
        print("Subscribed")
        self.subscription

    

    def listener_callback(self,msg):
        self.get_logger().info(f"msg: {msg.data}")

def main(args=None):
    rclpy.init(args=args)

    sub_temp = SubscribeTemperature()

    try:
        rclpy.spin(sub_temp)
    except KeyboardInterrupt:
        sub_temp.get_logger().info("Shutting down node...")
    finally:
        sub_temp.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()