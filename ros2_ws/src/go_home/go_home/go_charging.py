import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from thymiodirect import Connection
from thymiodirect import Thymio
from vicon_receiver.msg import PositionList
import time
import random
import json
import numpy as np
import socket
import sys

class GoCharging(Node):
    def __init__(self):
        super().__init__('go_charging')
        print("Initializing Thymio Robot")
        port = Connection.serial_default_port()
        th = Thymio(serial_port=port,
                    on_connect=lambda node_id: print(f'Thymio {node_id} is connected'))
        # Connect to Robot
        th.connect()
        self.robot = th[th.first_node()]
        self.start_time_ = time.time()

        # Delay to allow robot initialization of all variables
        time.sleep(1)
        # b) print all variables
        print(th.variables(th.first_node()))
        print("Robot connected")

        self.physical_ip = self.get_physical_ip()
        self.id= self.physical_ip.split('.')[-1]
        self.id=f'id{self.id}'
        # self.id = 'rob0'
        self.get_logger().info(f"Physical Ip={self.physical_ip}, id={self.id}")
        with open("wifi_id_mappings.json", "r") as f:
            wifi_id_mappings = json.load(f)
        self.id=wifi_id_mappings.get(self.id)

        self.get_logger().info(f"Updated ID from mapping: {self.id}")

        with open("vicon_angle_correction.json", "r") as f:
                self.corrections = json.load(f)

        with open("charging_destinatins.json", "r") as f:
                self.destinations = json.load(f)
        
        my_dest = self.destinations.get(self.id)
        my_dest = np.array(my_dest)
        print(my_dest)

        vicon_topic = "vicon/default/data"
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=rclpy.qos.HistoryPolicy.KEEP_LAST,
            depth=1
        )
        self.vicon_subscription =  self.create_subscription(
            PositionList,
            vicon_topic,
            self.vicon_callback,
            qos_profile
        )
        self.get_logger().info("Vicon sub done")

        # self.destination = np.array([-1000.0, -860.0])
        self.destination = my_dest
        self.threshold = 50.0
        # these gains you can tune:
        self.K_lin       = 0.5   # gain for distance
        self.K_ang       = 20.0   # gain for yaw error
        self.max_lin     = 200.0 # max forward speed
        self.max_ang     = 100.0 # max turning speed
        self.angle_tol = np.deg2rad(20.0)  # 20° in radians
        self.consecutive_ir_hits = 0
        self.collision_stop_time = 0
        self.get_logger().info("Init complete")

    def vicon_callback(self, msg):

        if time.time() - self.start_time_ > 1:

            self.start_time_ = time.time()
            for i in range(msg.n):
                # you are expected to set the id of each robot in the vicon system, you will receive it and compare here
                if msg.positions[i].subject_name == self.id:
                    self.my_position = msg.positions[i]
                    self.my_position_xy = [msg.positions[i].x_trans, msg.positions[i].y_trans]
                    vicon_yaw_radians = self.quaternion_to_yaw()
                    self.get_logger().info("Got message for my ID")
                    self.robot['leds.top'] = [0, 200, 0]

                    # self.my_vicon_yaw = vicon_yaw_radians * (180/np.pi) # rads to degrees

                    self.get_logger().info(f'**My Position= {self.my_position_xy}')
                    self.get_logger().info(f'My Yaw= {vicon_yaw_radians}')
                    if(self.my_position_xy[0] == 0.0 and self.my_position_xy[0] == 0.00):
                        self.robot['leds.top'] = [200, 0, 0]
                        self.robot['motor.left.target']  = -10
                        self.robot['motor.right.target'] = -10
                        continue
                    # 1) Compute vector to goal
                    vec = self.destination - np.array(self.my_position_xy)
                    dist = np.linalg.norm(vec)

                    self.get_logger().info(f'vec= {vec}')
                    self.get_logger().info(f'dist= {dist}')

                    if dist > self.threshold:
                        self.get_logger().info("distance higher than threshold")
                        # 2) Desired heading
                        target_theta = np.arctan2(vec[1], vec[0])
                        target_theta = target_theta - np.pi

                        # 5) angle error normalized to [-π,π]
                        err = (target_theta - vicon_yaw_radians + np.pi) % (2*np.pi) - np.pi
                        self.get_logger().info(f"Disered Heading: {target_theta}. Error in yaw yet: {err}")

                        # 4) Control law
                        if abs(err) > self.angle_tol:
                            # spin in place
                            turn_speed =  self.K_ang * err
                            self.get_logger().info(f"unbounded turn_speed: {turn_speed}")
                            if(turn_speed < -self.max_ang): turn_speed = -self.max_ang
                            if(turn_speed > self.max_ang): turn_speed = self.max_ang
                            if(turn_speed < 0 and abs(turn_speed) < 10): turn_speed = -10
                            if(turn_speed > 0 and abs(turn_speed) < 10): turn_speed = 10
                            left_spd  = -turn_speed
                            right_spd =  turn_speed
                            self.get_logger().info(f"spin in place (turn_speed:{turn_speed}): leftspeed:{int(left_spd)}, rightspeed:{int(right_spd)}")
                        else:
                            # drive forward
                            fwd_speed = np.clip(self.K_lin * dist,
                                                0, self.max_lin)
                            if(fwd_speed < 10): fwd_speed = 10
                            left_spd  = fwd_speed
                            right_spd = fwd_speed
                            self.get_logger().info(f"Move forward: leftspeed:{int(left_spd)}, rightspeed:{int(right_spd)}")

                        # send to motors
                        readings = self.robot['prox.horizontal'][:5]
                        self.get_logger().info(f"Prox Readings: {readings}")
                        # obtacle and command to move forward
                        if any(r > 800 for r in readings) and left_spd == right_spd:
                            self.robot['motor.left.target']  = 0
                            self.robot['motor.right.target'] = 0
                            if(time.time() - self.collision_stop_time > 5):
                                move_time = time.time()
                                #move back
                                while time.time() - move_time < 3:
                                    self.robot['motor.left.target']  = -150
                                    self.robot['motor.right.target'] = -150
                                move_time = time.time()
                                # rotate
                                while time.time() - move_time < 3:
                                    self.robot['motor.left.target']  = -150
                                    self.robot['motor.right.target'] = 150
                                self.collision_stop_time = time.time()
                        else:
                            self.collision_stop_time = time.time()
                            self.robot['motor.left.target']  = int(left_spd)
                            self.robot['motor.right.target'] = int(right_spd)

                    else:
                        # 5) Close enough, stop
                        self.robot['motor.left.target']  = 0
                        self.robot['motor.right.target'] = 0
                        self.robot['leds.top'] = [0, 0, 200]
                        self.get_logger().info("Reached destination, stopping.")
                        raise Exception

    def get_physical_ip(self):
        try:
            # Connect to an external host to get the local network IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # Using Google's DNS server
                ip_address = s.getsockname()[0]
            return ip_address
        except Exception as e:
            return f"Error: {e}"
        
    def stop(self):
        self.robot['motor.left.target']  = 0
        self.robot['motor.right.target'] = 0
        self.get_logger().info("Motion Stopped")

        
    def quaternion_to_yaw(self):
        """Convert a quaternion (x, y, z, w) to a yaw angle (in radians)."""
        w = round(self.my_position.w, 4)
        x_rot = round(self.my_position.x_rot,4)
        y_rot = round(self.my_position.y_rot,4)
        z_rot = round(self.my_position.z_rot, 4)
        # self.get_logger().info(f"w={w} x_rot={x_rot}  y_rot={y_rot} z_rot={z_rot}")
        yaw = np.arctan2(2 * (w * z_rot + x_rot * y_rot), 1 - 2 * (y_rot ** 2 + z_rot ** 2))
        # yaw_degrees = np.degrees(yaw)
        # print('calculated yaw: %f' %(yaw_degrees % 360))
        return yaw + self.corrections.get(self.id)





def main(args=None):

    try:
        rclpy.init(args=args)

        go_to_home = GoCharging()
        rclpy.spin(go_to_home)

    except KeyboardInterrupt:
        go_to_home.stop()
        go_to_home.get_logger().info("Stopping, Keyboard Interrupt")
        go_to_home.destroy_node()
    except Exception:
        go_to_home.stop()
        go_to_home.get_logger().info("Stopping, exception")
        go_to_home.destroy_node()
    finally:
        go_to_home.get_logger().info("rclpy shutdown")
        rclpy.shutdown()
        go_to_home.get_logger().info("System Exit")
        sys.exit(0)
        

