import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from vicon_receiver.msg import Position
from vicon_receiver.msg import PositionList
import math

class ReceiveDecide(Node):
    def __init__(self):
        super().__init__('receive_decide')
        vicon_topic = "vicon/default/data"
        self.vicon_subscription =  self.create_subscription(
            PositionList,
            vicon_topic,
            self.vicon_callback,
            10
        )

        self.my_position = None
        self.neighbours_by_id = set()
        self.all_robots_position_by_id_vicon = dict()
        self.neighbourhood_size = 5
        self.informed = True
        self.neighbour_distance_mm = 200 #so 20 cm
        self.social_info_counts = dict()
        self.neighbours_opinions = dict()

        self.subscription = self.create_subscription(
            String,
            'wind_direction',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        id = msg.data.split(':')[0]
        wind_direction = msg.data.split(':')[1]

        print(f'Received from {id}, wind direction {wind_direction}')

        #Check if this robot is in close proximity to us, this info comes from the vicon system
        if id in self.neighbours_by_id:
            self.neighbours_opinions[id] = wind_direction
        self.get_logger().info(f"msg: {msg.data}")
        # Sound logic, decision making would be triggered only after receiving of some message, so record temp after receiving message ie. calculate quad based on
        # sensor input
        self.my_quadrant_from_sensor = self.get_quad_from_temp()
        if(len(self.neighbours_opinions) == self.neighbourhood_size):
            self.make_quad_opinion()

    def vicon_callback(self, msg):
        if self.timer_ % 1 == 0:
            print("vicon message")
            self.neighbours_by_id = set()
            for i in range(msg.n):
                # you are expected to set the id of each robot in the vicon system, you will receive it and compare here
                if int(msg.positions[i].subject_name) == self.id:
                    self.my_position = [msg.positions[i].x_trans, msg.positions[i].y_trans]
                else:
                    self.all_robots_position_by_id_vicon[int(msg.positions[i].subject_name)] = [self.positions[i].x_trans, self.positions[i].y_trans]
            for id_vicon in self.all_robots_position_by_id_vicon:
                if self.check_distance(self.my_position, self.all_robots_position_by_id_vicon[id_vicon]):
                    self.neighbours_by_id.add(id_vicon)

    def check_distance(self, my_pos, neighbour_pos):
        distance = math.sqrt((neighbour_pos[0] - my_pos[0])**2 + (neighbour_pos[1] - my_pos[1])**2)
        if distance < self.neighbour_distance_mm:
            return True
        return False
    
    def majority_vote(self):
        self.social_info_counts.clear()

        for quad_vals in self.neighbours_opinions.values():
            if quad_vals in self.social_info_counts:
                self.social_info_counts[quad_vals] += 1
            else:
                self.social_info_counts[quad_vals] = 1


def main(args=None):
    rclpy.init(args=args)

    receive_decide = ReceiveDecide()

    try:
        rclpy.spin(receive_decide)
    except KeyboardInterrupt:
        receive_decide.get_logger().info("Shutting down node...")
    finally:
        receive_decide.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
