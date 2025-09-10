import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import random
import os
import glob
import time
import socket
from vicon_receiver.msg import Position
from vicon_receiver.msg import PositionList
import math
class TempDecision(Node):
    def __init__(self):
        super.__init__('temp_decision')
        # Declare parameter is to be used with a launch file
        # self.declare_parameter('default_topic', rclpy.Parameter.Type.STRING)
        vicon_topic = "vicon/default/data"
        #Init temp read
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'

        pub_topic = 'hot_quad_topic'
        self.physical_ip = self.get_physical_ip()
        self.id= self.physical_ip[len(self.physical_ip)-3:]
        print(f"Physical Ip={self.physical_ip}, id={self.id}")

        # I will format the string "Id:1 Q:3"
        #TODO: Write hot_quad_listener_callback function
        self.subscription = self.create_subscription(
            String,
            pub_topic,
            self.hot_quad_listener_callback,
            10
        )
        self.vicon_subscription =  self.create_subscription(
            PositionList,
            vicon_topic,
            self.vicon_callback,
            10
        )
        self.publisher = self.create_publisher(String,
                                               pub_topic,
                                               10)
        self.timer = self.create_timer(10,self.publish_opinion)
        print(f"Subscribed to {pub_topic}")

        self.personal_info_weight = 0.6
        # self.neighbourhood_size = 5
        self.informed = True
        # Will be a list with my x and y axis position
        self.my_position = None
        self.neighbour_distance_mm = 200 #so 20 cm
        self.my_opinion = random.randint(1,4)
        self.all_robots_position_by_id_vicon = dict()
        self.neighbours_by_id = set()
        self.neighbours_opinion = dict()
        self.quads_visited = set()
        self.higest_temp_each_quad = {1:-50, 2:-50, 3:-50, 4:-50}
        self.social_info_counts = dict()
    
    def publish_opinion(self):
        # If 4 quads are already visited then send opinion
        if(len(self.quads_visited) == 4):
            # Trigger decision making here
            self.make_quad_opinion()
            msg = String()
            msg.data = f"Id:{self.id} Q:{self.my_opinion}"
            self.publisher.publish(msg)
            self.get_logger().info(f"Publishing: {msg.data}")
            self.quads_visited = set()
    
    def vicon_callback(self, msg):
        if self.timer_ % 1 == 0:
            print("vicon message")
            self.neighbours_by_id.clear()
            for i in range(msg.n):
                # you are expected to set the id of each robot in the vicon system, you will receive it and compare here
                if int(msg.positions[i].subject_name) == self.id:
                    self.my_position = [self.positions[i].x_trans, self.positions[i].y_trans]
                    self.quadrant_tracker(self.my_position)
                else:
                    # A dict keyed by id to store the postion of other robots
                    self.all_robots_position_by_id_vicon[int(msg.positions[i].subject_name)] = [self.positions[i].x_trans, self.positions[i].y_trans]
            for id_vicon in self.all_robots_position_by_id_vicon:
                if self.check_distance(self.my_position, self.all_robots_position_by_id_vicon[id_vicon]):
                    self.neighbours_by_id.add(id_vicon)

    def check_distance(self,my_pos, neighbour_pos):
        distance = math.sqrt((neighbour_pos[0] - my_pos[0])**2 + (neighbour_pos[1] - my_pos[1])**2)
        if distance < self.neighbour_distance_mm:
            return True
        return False
    
    def quadrant_tracker(self, position):
        temp_sensor_reading = -50
        if(self.informed):
            temp_sensor_reading = self.get_temp_c()
        ## It is assumed that the range is 500, probably quite different in real life
        if (position[0] > -500 and position[0] < 0) and (position[1] > 0 and position[1] < 500):
            if(temp_sensor_reading > self.higest_temp_each_quad[1]): self.higest_temp_each_quad[1] = temp_sensor_reading
            # We say we are in quad 1
            self.quads_visited.add(1)
        elif (position[0] > 0 and position[0] < 500) and (position[1] > 0 and position[1] < 500):
            if(temp_sensor_reading > self.higest_temp_each_quad[2]): self.higest_temp_each_quad[2] = temp_sensor_reading
            # We say we are in quad 2
            self.quads_visited.add(2)
        elif (position[0] > 0 and position[0] < 500) and (position[1] > -500 and position[1] < 0):
            if(temp_sensor_reading > self.higest_temp_each_quad[3]): self.higest_temp_each_quad[3] = temp_sensor_reading
            # We say we are in quad 3
            self.quads_visited.add(3)
        elif (position[0] > -500 and position[0] < 0) and (position[1] > -500 and position[1] < 0):
            if(temp_sensor_reading > self.higest_temp_each_quad[4]): self.higest_temp_each_quad[4] = temp_sensor_reading
            # We say we are in quad 4
            self.quads_visited.add(4)
        else:
            self.get_logger().info(f"ID: {self.id} In no quad, how is this possible, check")
    
    def get_physical_ip(self):
        try:
            # Connect to an external host to get the local network IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # Using Google's DNS server
                ip_address = s.getsockname()[0]
            return ip_address
        except Exception as e:
            return f"Error: {e}"
        
    def get_temp_c(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        lines = self.__read_temp_raw()
        while lines[0].strip()[-3:] != 'YES':
            time.sleep(0.2)
            lines = self.__read_temp_raw()
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos + 2:]
            temp_c = float(temp_string) / 1000.0
            return temp_c
        return None
    
    def majority_vote(self):
        self.social_info_counts.clear()

        # The value in neighbours_opinion is q_val, for each q_val we increment the counter by 1
        for quad_vals in self.neighbours_opinion.values():
            if quad_vals in self.social_info_counts:
                self.social_info_counts[quad_vals] += 1
            else:
                self.social_info_counts[quad_vals] = 1

    def make_quad_opinion(self):
        # in case there are no opinions from the neighbours the decision making process is basically giving a random quad as count for all will be 0
        quad_personal_opinion = self.get_highest_in_dict(self.higest_temp_each_quad)
        self.majority_vote()
        m = len(self.social_info_counts)
        decision_dict = dict()
        for quad in [1,2,3,4]:
            if self.informed:
                mi = self.social_info_counts.get(quad,0)

                decision_dict[quad] = mi + (self.personal_info_weight
                                            * m * 
                                            (1 if quad == quad_personal_opinion else 0))
        
        if self.informed:
            self.my_opinion = self.get_highest_in_dict(decision_dict)
        else:
            self.my_opinion = self.get_highest_in_dict(self.social_info_counts)


        
    def hot_quad_listener_callback(self, msg):
        split_msg = msg.split()
        id_part = int(split_msg[0].split(":")[1])  # Extract and convert Id to integer
        q_part = int(split_msg[1].split(":")[1])   # Extract and convert Q to integer
        self.neighbours_opinion.clear()
        #Check if this robot is in close proximity to us, this info comes from the vicon system
        if id_part in self.neighbours_by_id:
            self.neighbours_opinion[id_part] = q_part
            self.get_logger().info(f"msg: {msg.data}")

    def get_highest_in_dict(self, the_dict):
        max_count = max(the_dict.values())
        keys_with_max_count = [key for key, value in the_dict.items() if value == max_count]

        if len(keys_with_max_count) > 1:
            return random.choice(keys_with_max_count)
        else:
            return keys_with_max_count[0]
