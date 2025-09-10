import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
import subprocess
import cv2
import numpy as np
from std_msgs.msg import String
from vicon_receiver.msg import Position
from vicon_receiver.msg import PositionList
from scipy.spatial.transform import Rotation as R
import math
import socket
import time
import datetime
import csv
import json

class PublishWindDirection(Node):
    def __init__(self):
        super().__init__('publish_wind_direction')
        self.physical_ip = self.get_physical_ip()
        self.id= self.physical_ip.split('.')[-1]
        # if self.physical_ip.split('.')[-2] == "231" and self.physical_ip.split('.')[-1] == "193":
        #     self.id = "1193"
        self.id=f'id{self.id}'
        # self.id = 'rob0'
        self.get_logger().info(f"Physical Ip={self.physical_ip}, id={self.id}")
        with open("wifi_id_mappings.json", "r") as f:
            wifi_id_mappings = json.load(f)
        self.id=wifi_id_mappings.get(self.id)

        self.get_logger().info(f"Updated ID from mapping: {self.id}")
        
        print("CV2 Ver. = ", cv2.__version__)
        self.lens_position = 8
        vicon_topic = "vicon/default/data"
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=rclpy.qos.HistoryPolicy.KEEP_LAST,
            depth=1
        )
        self.publisher_ = self.create_publisher(String, f'wind_direction/{self.id}', qos_profile)
        self.get_logger().info(f"Publsihing on: wind_direction/{self.id}")
        # self.publisher_ = self.create_publisher(String, 'wind_direction', qos_profile)
        # timer_period = 1.0  # seconds
        # self.timer = self.create_timer(timer_period, self.timer_callback)

        self.vicon_subscription =  self.create_subscription(
            PositionList,
            vicon_topic,
            self.vicon_callback,
            qos_profile
        )

        self.get_logger().info(f"Subscribed to: {vicon_topic}")
        self.vicon_rad_readings = dict()
        # self.subscription = self.create_subscription(
        #     String,
        #     'wind_direction',
        #     self.listener_callback,
        #     qos_profile
        # )

        thymio_ips = ['id68','id136','id137','id142','id151','id152','id155','id189','id192','id193','id194','id195','id200','id206',
                      'id207','id223','id224','id236','id247','id1193']
        # thymio_ips = ['id136','id195','id151','id207','id224','id192','id193','id142','id206','id194','id137','id223']
        self.other_devices = [i for i in thymio_ips if i != self.id]
        for dev in self.other_devices:
            topic_name = f'wind_direction/{dev}'
            self.create_subscription(
                String,
                topic_name,
                self.listener_callback,
                qos_profile
            )
            self.get_logger().info(f'Subscribed to: {topic_name}')

        


        with open("vicon_angle_correction.json", "r") as f:
                self.corrections = json.load(f)

        self.my_position_xy = None
        self.neighbours_by_id = set()
        self.all_robots_position_by_id_vicon = dict()
        self.neighbourhood_size = 3
        self.informed = True
        self.neighbour_distance_mm = 700 #so 80 cm
        self.social_info_counts = dict()
        self.neighbours_opinions = dict()
        self.all_opinions = dict() # Keep track of all opinions you have received until now, there are cases where a robot is in neighbourhood but not publishing at that exact moment, these should not be missed
        self.personal_info_weight = 0.4

        with open("uninformed_mapping.json", "r") as f:
            uniformed_mapping = json.load(f)
        
        if(uniformed_mapping.get(self.id)==0): self.personal_info_weight=0.0

        self.commnunication_noise = 0.2

        self.my_position = None
        self.my_vicon_yaw = 0.0
        self.my_wind_direction = np.random.choice(['N','S','E','W'])
        self.cam_angle = -999.0
        # Random wind direction init
        self.my_wind_direction_opinion = np.random.choice(['N','S','E','W'])
        self.start_time_ = time.time()
        self.node_start_time = time.time()
        self.csv_file = f"log_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        self.csv_index = 0
        self.runtime = 600
        self.init_csv()

    def init_csv(self):
        # Always overwrite the file at the start of the node
        with open(self.csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['index', 'timestamp', 'message', 'cam_wind_direction'])
        

    def listener_callback(self, msg):
        # This is listening to the wind_direction topic, if someone publishes there opinion, we listen here
        # Once we have enough unique opinions, we trigger the decision making
        start_t = time.time()
        id = msg.data.split(':')[0]
        wind_direction = msg.data.split(':')[1]
        if id == self.id: return # Return incase it is your own message

        self.get_logger().info(f'* Received from {id}, wind direction {wind_direction}')
        if id != self.id:
            # Simulate communication noise
            if np.random.random() < self.commnunication_noise:
                other_opinions = [opinion for opinion in ['N','S','E','W'] if opinion!=wind_direction]
                wind_direction = np.random.choice(other_opinions)
                self.get_logger().info(f"Comm. Noise, new received opinion: {wind_direction}")
            self.all_opinions[id] = wind_direction
        self.get_logger().info(f"All opinions = {self.all_opinions}")

        #Check if this robot is in close proximity to us, this info comes from the vicon system
        self.get_logger().info(f"Publisher, neighbours_by_id={self.neighbours_by_id}")
        if id in self.neighbours_by_id:
            self.neighbours_opinions[id] = self.all_opinions[id] # Get the opinion of the neighbour
        # Sound logic, decision making would be triggered only after receiving of some message, so record temp after receiving message ie. calculate quad based on
        # sensor input
        self.cam_angle = self.process_image_get_direction()
        self.get_true_wind_direction(self.cam_angle)
        self.get_logger().info(f"Publisher, Neighbourhood size: {len(self.neighbours_by_id)}")
        if(len(self.neighbours_by_id) >= self.neighbourhood_size):
            self.get_logger().info('Decision Making Triggered')
            self.get_logger().info(f"Publisher, Neighbours Opinion: {len(self.neighbours_opinions)}")
            self.make_wind_direction_opinion()
        self.get_logger().info(f"Time taken for picture and decision making: {time.time()-start_t}")
    
    # def timer_callback(self):
    #     # Publishing stuff to the wind_direction topic
    #     msg = String()
    #     start_t = time.time()

    #     if time.time() - self.node_start_time > 600:
    #         self.get_logger().info('Raising exception')
    #         raise Exception

    #     msg.data = f"{self.id}:{self.my_wind_direction_opinion}"
    #     self.publisher_.publish(msg)
    #     self.get_logger().info(f'Publishing: {msg.data}, Time needed to publish: {time.time()-start_t}, Starttime:{start_t}')

    def vicon_callback(self, msg):

        if time.time() - self.start_time_ > 0.1:

            self.start_time_ = time.time()
            for i in range(msg.n):
                # you are expected to set the id of each robot in the vicon system, you will receive it and compare here
                if msg.positions[i].subject_name == self.id:
                    self.my_position = msg.positions[i]
                    self.my_position_xy = [msg.positions[i].x_trans, msg.positions[i].y_trans]
                    vicon_yaw_radians = self.quaternion_to_yaw()

                    self.my_vicon_yaw = vicon_yaw_radians * (180/np.pi) # rads to degrees

                    self.get_logger().info(f'Vicon Position= {self.my_position_xy}')

                else:
                    # self.get_logger().info(f'msg={msg}')
                    self.all_robots_position_by_id_vicon[msg.positions[i].subject_name] = [msg.positions[i].x_trans, msg.positions[i].y_trans]
            self.neighbours_by_id.clear() # clear to keep updated the neighbours and remove old ones
            for id_vicon in self.all_robots_position_by_id_vicon:
                # print(f"My Pos {self.my_position_xy}, All Robs: {self.all_robots_position_by_id_vicon}")
                if self.all_robots_position_by_id_vicon[id_vicon] == [0,0]: continue
                if self.check_distance(self.my_position_xy, self.all_robots_position_by_id_vicon[id_vicon]):
                    self.neighbours_by_id.add(id_vicon)
            self.get_logger().info(f"Neighbourhood size: {len(self.neighbours_by_id)}")
            # To induce decision making, we need something to publish something first, then publishing will continue
            if self.csv_index == 0:
                m_rand = String()
                m_rand.data = f"{self.id}:{self.my_wind_direction_opinion}"
                self.publisher_.publish(m_rand)
            # print(f"My Pos {self.my_position_xy} My current neighbours: {self.neighbours_by_id}")
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            self.get_logger().info(f"TIME: Vicon pose update at: {current_time}")

    def make_wind_direction_opinion(self):
        self.majority_vote()
        m = len(self.neighbours_opinions)
        self.get_logger().info(f"Inside Decision Making, neighbours opinion: {self.neighbours_opinions}")
        self.get_logger().info(f"Inside Decision Making, social opinions: {self.social_info_counts}")
        decision_dict = dict()
        self.get_logger().info(f"Inside Decision Making, My Wind Direction: {self.my_wind_direction}")
        for direction in ['N','S','E','W']:
            if self.informed:
                mi = self.social_info_counts.get(direction,0)

                decision_dict[direction] = mi + (self.personal_info_weight
                                            * m * 
                                            (1 if direction == self.my_wind_direction else 0))

        
        if self.informed:
            self.get_logger().info(f"Inside Decision Making, Decision dict: {decision_dict}")
            self.my_wind_direction_opinion = self.get_highest_in_dict(decision_dict)
        else:
            self.get_logger().info(f"Uninformed decision making: {self.social_info_counts}")
            self.my_wind_direction_opinion = self.get_highest_in_dict(self.social_info_counts)
        
        timestamp = datetime.datetime.now().isoformat()
        self.csv_index += 1
        # Log to CSV
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([self.csv_index, timestamp, self.my_wind_direction_opinion, self.my_wind_direction])

        # Publishing stuff to the wind_direction topic
        msg = String()

        if time.time() - self.node_start_time > self.runtime:
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M:%S")
            self.get_logger().info(f'Raising exception at {current_time}')
            raise Exception

        msg.data = f"{self.id}:{self.my_wind_direction_opinion}"
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M:%S")
        self.get_logger().info(f"TIME: Decision making completed at: {current_time}.")
        self.get_logger().info(f"-----------------------------------------------------")

    def get_highest_in_dict(self, the_dict):
        max_count = max(the_dict.values())
        keys_with_max_count = [key for key, value in the_dict.items() if value == max_count]

        if len(keys_with_max_count) > 1:
            return np.random.choice(keys_with_max_count)
        else:
            return keys_with_max_count[0]
        
    

    def check_distance(self, my_pos, neighbour_pos):
        distance = math.sqrt((neighbour_pos[0] - my_pos[0])**2 + (neighbour_pos[1] - my_pos[1])**2)
        if distance < self.neighbour_distance_mm:
            return True
        return False

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
    
    
    def get_true_wind_direction(self, cam_angle):
        ground_truth_wind_direction = (cam_angle + self.my_vicon_yaw) % 360
        self.get_logger().info(f"***Cam angle= {cam_angle}, vico ang deg= {self.my_vicon_yaw} Ground Truth= {ground_truth_wind_direction}")
        self.my_wind_direction = '1'
        if (ground_truth_wind_direction < 45 and ground_truth_wind_direction >= 0) or (ground_truth_wind_direction < 360 and ground_truth_wind_direction >= 315):
            self.my_wind_direction = 'N'
        if ground_truth_wind_direction >= 225 and ground_truth_wind_direction < 315:
            self.my_wind_direction = 'E'
        if ground_truth_wind_direction >= 135 and ground_truth_wind_direction < 225:
            self.my_wind_direction = 'S'
        if ground_truth_wind_direction >= 45  and ground_truth_wind_direction < 135:
            self.my_wind_direction = 'W'
        if self.my_wind_direction == '1':
            self.my_wind_direction = np.random.choice(['N','S','E','W'])
        # self.get_logger().info(f"***Corrected Wind Direction= {self.my_wind_direction}")
        

    def majority_vote(self):
        self.social_info_counts.clear()
        for wind_dir in self.neighbours_opinions.values():
            if wind_dir in self.social_info_counts:
                self.social_info_counts[wind_dir] += 1
            else:
                self.social_info_counts[wind_dir] = 1
        


    def get_physical_ip(self):
        try:
            # Connect to an external host to get the local network IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # Using Google's DNS server
                ip_address = s.getsockname()[0]
            return ip_address
        except Exception as e:
            return f"Error: {e}"
    
    def my_estimatePoseSingleMarkers(self, corners, marker_size, mtx, distortion):
        '''
        This will estimate the rvec and tvec for each of the marker corners detected by:
        corners, ids, rejectedImgPoints = detector.detectMarkers(image)
        corners - is an array of detected corners for each detected marker in the image
        marker_size - is the size of the detected markers
        mtx - is the camera matrix
        distortion - is the camera distortion matrix
        RETURN list of rvecs, tvecs, and trash (so that it corresponds to the old estimatePoseSingleMarkers())
        '''
        marker_points = np.array([[-marker_size / 2, marker_size / 2, 0],
                                [marker_size / 2, marker_size / 2, 0],
                                [marker_size / 2, -marker_size / 2, 0],
                                [-marker_size / 2, -marker_size / 2, 0]], dtype=np.float32)
        trash = []
        rvecs = []
        tvecs = []
        
        for c in corners:
            nada, R, t = cv2.solvePnP(marker_points, c, mtx, distortion, False, cv2.SOLVEPNP_IPPE_SQUARE)
            rvecs.append(R)
            tvecs.append(t)
            trash.append(nada)
        return rvecs, tvecs, trash
    
    
    def get_marker_rotation_angle(self, rvec):
        # Convert rotation vector to rotation matrix, this uses the Rodrigues rotation formula
        R, _ = cv2.Rodrigues(rvec)
        # print(R)

        # Extract yaw angle (rotation around Z-axis)
        yaw = np.arctan2(R[1, 0], R[0, 0])  # R[1,0] = sin(theta), R[0,0] = cos(theta)
        
        # Convert to degrees
        yaw_degrees = np.degrees(yaw)
        
        return yaw_degrees
    
    def process_image_get_direction(self, img_name='cam_pic.jpg'):
        self.take_picture(img_name)
        time.sleep(2)
        print("--Processing Picture--")
        # Load the image
        image = cv2.imread(f'{img_name}')

        # Define the dictionary
        aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
        parameters = cv2.aruco.DetectorParameters()

        # Detect ArUco markers
        detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
        corners, ids, rejected = detector.detectMarkers(image)
        # print(corners)

        if ids is not None:
            # Draw detected markers
            cv2.aruco.drawDetectedMarkers(image, corners, ids, (0,0,225))
        else:
            print("No ArUco marker detected.")

        camera_calib_data = np.load('camera_calibration_data.npz')
        camera_matrix = camera_calib_data['camera_matrix']
        dist_coeffs = camera_calib_data['dist_coeffs']

        marker_length = 0.02375 #in meters, it is 23.75mm
        angle_degrees = -999.0
        true_cam_angle = -999.0
        if ids is not None:
            rvec, tvec, _ = self.my_estimatePoseSingleMarkers(corners, marker_length, camera_matrix, dist_coeffs)
            for idx in range(len(ids)):
                cv2.drawFrameAxes(image, camera_matrix, dist_coeffs, rvec[idx], tvec[idx], 0.05)
                angle_degrees= self.get_marker_rotation_angle(rvec[idx])

                #angle_degrees is at a 90 degree offset to robot front as the cam is mounted at 90 degrees, also the angles range from 0-180 and -1 to -180
                true_cam_angle = angle_degrees - 90
                # if true_cam_angle < 0 : true_cam_angle = true_cam_angle + 360
                # print("Angle = ",angle_degrees)
        image = cv2.putText(image, f'Angle={true_cam_angle:.2f}', (1296,972), cv2.FONT_HERSHEY_SIMPLEX, 
                   fontScale=2, color=(5, 10, 255), thickness=5, lineType=cv2.LINE_AA)
        cv2.imwrite(f'processed_{img_name}', image)
        print("--Picture Processing Done--")
        return true_cam_angle
        
    def take_picture(self, save_image_name):
        print("--Taking picture--")
        
        tuning_file = "af_jsons/ov5647_af.json"
        # Run the libcamera-still command with autofocus configuration
        command = [
            "libcamera-still",
            "-o", save_image_name,
            "--immediate",
            "--autofocus-mode", "manual",
            "--lens-position", str(self.lens_position),
            "--tuning-file", tuning_file
        ]

        try:
            subprocess.run(command, check=True, stdout = subprocess.DEVNULL, stderr = subprocess.STDOUT, timeout=10)
        except subprocess.TimeoutExpired:
            print("--Timeout: libcamera-still took too long. Skipping this attempt.")
        except subprocess.CalledProcessError as e:
            print(f"Error capturing image: {e}")

def main(args=None):

    try:
        rclpy.init(args=args)

        wind_direction_sensor = PublishWindDirection()

        rclpy.spin(wind_direction_sensor)

        # Destroy the node explicitly
        # (optional - otherwise it will be done automatically
        # when the garbage collector destroys the node object)
        # wind_direction_sensor.destroy_node()
        # rclpy.shutdown()
    except KeyboardInterrupt:
        wind_direction_sensor.get_logger().info("Stopping, Keyboard Interrupt")
        wind_direction_sensor.destroy_node()
    except Exception:
        wind_direction_sensor.get_logger().info("Publisher stopping, exception")
        wind_direction_sensor.destroy_node()
    finally:
        rclpy.shutdown()



# if __name__ == '__main__':
#     main()
