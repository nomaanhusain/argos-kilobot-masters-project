import rclpy
from rclpy.node import Node
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

class PublishWindDirection(Node):
    def __init__(self):
        super().__init__('publish_wind_direction')
        self.physical_ip = self.get_physical_ip()
        self.id= self.physical_ip.split('.')[-1]
        self.id=f'id{self.id}'
        self.id = 'rob0'
        print(f"Physical Ip={self.physical_ip}, id={self.id}")
        print("CV2 Ver. = ", cv2.__version__)
        self.lens_position = 6
        vicon_topic = "vicon/default/data"
        self.publisher_ = self.create_publisher(String, 'wind_direction', 10)
        timer_period = 3  # seconds
        self.timer = self.create_timer(timer_period, self.timer_callback)

        self.vicon_subscription =  self.create_subscription(
            PositionList,
            vicon_topic,
            self.vicon_callback,
            10
        )
        self.vicon_rad_readings = dict()
        self.subscription = self.create_subscription(
            String,
            'wind_direction',
            self.listener_callback,
            10
        )

        self.my_position_xy = None
        self.neighbours_by_id = set()
        self.all_robots_position_by_id_vicon = dict()
        self.neighbourhood_size = 5
        self.informed = True
        self.neighbour_distance_mm = 200 #so 20 cm
        self.social_info_counts = dict()
        self.neighbours_opinions = dict()
        self.personal_info_weight = 0.6

        self.my_position = None
        self.my_vicon_yaw = 0.0
        self.my_wind_direction = None
        self.vicon_angle_offset = -35
        self.cam_angle = -999.0
        # Random wind direction init
        self.my_wind_direction_opinion = np.random.choice(['N','S','E','W'])
        self.timer_ = 0
        self.start_time_ = time.time()

    def listener_callback(self, msg):
        # This is listening to the wind_direction topic, if someone publishes there opinion, we listen here
        # Once we have enough unique opinions, we trigger the decision making
        id = msg.data.split(':')[0]
        wind_direction = msg.data.split(':')[1]

        print(f'Received from {id}, wind direction {wind_direction}')
        print("**************************")

        #Check if this robot is in close proximity to us, this info comes from the vicon system
        if id in self.neighbours_by_id:
            self.neighbours_opinions[id] = wind_direction
        # self.get_logger().info(f"msg: {msg.data}")
        # Sound logic, decision making would be triggered only after receiving of some message, so record temp after receiving message ie. calculate quad based on
        # sensor input
        #TODO: Get the angle here, comment now for testing Vicon angle
        self.cam_angle = self.process_image_get_direction()
        # self.cam_angle = 0
        self.get_true_wind_direction(self.cam_angle)
        if(len(self.neighbours_opinions) == self.neighbourhood_size):
            self.make_wind_direction_opinion()
    
    def timer_callback(self):
        # Publishing stuff to the wind_direction topic
        msg = String()
        # self.cam_angle = self.process_image_get_direction()
        # self.cam_angle = 90.0
        # print("cam angle= ",self.cam_angle)
        # self.get_true_wind_direction(self.cam_angle)
        # print(f"Id:{self.id}, Angle:{self.my_wind_direction_opinion}")
        msg.data = f"{self.id}:{self.my_wind_direction_opinion}"
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)

    def vicon_callback(self, msg):
        if time.time() - self.start_time_ > 2:
        # if self.timer_ % 1000 == 0:
            print("vicon message received")
            self.start_time_ = time.time()
            for i in range(msg.n):
                # you are expected to set the id of each robot in the vicon system, you will receive it and compare here
                if msg.positions[i].subject_name == self.id:
                    self.my_position = msg.positions[i]
                    self.my_position_xy = [msg.positions[i].x_trans, msg.positions[i].y_trans]
                    vicon_yaw_radians = self.quaternion_to_yaw()
                    # self.vicon_rad_readings[time.time()] = vicon_yaw_radians
                    # vicon_yaw_radians = self.quat_to_yaw()
                    self.my_vicon_yaw = vicon_yaw_radians * (180/np.pi) # rads to degrees
                    offset = -165 # offset to correct the difference from the vicon output, so what I expect to be 0 is outputted as -165 so i just sub that
                    # self.my_vicon_yaw = self.my_vicon_yaw - self.vicon_angle_offset
                    # self.my_vicon_yaw = self.my_vicon_yaw % 360
                    self.get_logger().info(f'--------------------')
                    # self.get_logger().info(f"w={self.my_position.w} x_rot={self.my_position.x_rot}  y_rot={self.my_position.y_rot} z_rot={self.my_position.z_rot}")
                    self.get_logger().info(f'Vicon Yaw Rads= {vicon_yaw_radians}')
                    self.get_logger().info(f'** Vicon Yaw Degrees= {self.my_vicon_yaw}')
                    # print("vicon rad  hist= ",self.vicon_rad_readings)
                    self.get_logger().info(f'Vicon Position= {self.my_position_xy}')
                    # self.get_logger().info(f'my_Id_msg={msg}')
                    self.get_logger().info(f'--------------------')
                else:
                    # self.get_logger().info(f'msg={msg}')
                    self.all_robots_position_by_id_vicon[msg.positions[i].subject_name] = [msg.positions[i].x_trans, msg.positions[i].y_trans]
            for id_vicon in self.all_robots_position_by_id_vicon:
                if self.check_distance(self.my_position_xy, self.all_robots_position_by_id_vicon[id_vicon]):
                    self.neighbours_by_id.add(id_vicon)
            self.timer_ = 0
        else:
            # self.timer_ = self.timer_ + 1
            self.timer_ = 0

    def make_wind_direction_opinion(self):
        self.majority_vote()
        m = len(self.neighbours_opinions)
        decision_dict = dict()
        for direction in ['N','S','E','W']:
            if self.informed:
                mi = self.social_info_counts.get(direction,0)

                decision_dict[direction] = mi + (self.personal_info_weight
                                            * m * 
                                            (1 if direction == self.my_wind_direction else 0))
                
        if self.informed:
            self.my_wind_direction_opinion = self.get_highest_in_dict(decision_dict)
        else:
            self.my_wind_direction_opinion = self.get_highest_in_dict(self.social_info_counts)

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
        # if w < 0: w = w * -1.0
        # if x_rot < 0: x_rot = x_rot * -1.0
        # if y_rot < 0: y_rot = y_rot * -1.0
        # if z_rot < 0: z_rot = z_rot * -1.0
        self.get_logger().info(f"w={w} x_rot={x_rot}  y_rot={y_rot} z_rot={z_rot}")
        yaw = np.arctan2(2 * (w * z_rot + x_rot * y_rot), 1 - 2 * (y_rot ** 2 + z_rot ** 2))
        yaw_degrees = np.degrees(yaw)
        print('calculated yaw: %f' %(yaw_degrees % 360))
        return yaw
    
    
    def get_true_wind_direction(self, cam_angle):
        ground_truth_wind_direction = (cam_angle + self.my_vicon_yaw) % 360
        self.get_logger().info(f"***Cam angle= {cam_angle}, vico ang= {self.my_vicon_yaw} Ground Truth= {ground_truth_wind_direction}")
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
            print('taking random opinion as angle could not be read')
            self.my_wind_direction = np.random.choice(['N','S','E','W'])
        self.get_logger().info(f"***Corrected Wind Direction= {self.my_wind_direction}")
        

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
            (topLeft, topRight, bottomRight, bottomLeft) = corners[0][0]
            # print(f"Image Name={img_name}: ")
            # print(topLeft, topRight, bottomLeft, bottomRight)
            # cv2.namedWindow("Detected_ArUco_Marker", cv2.WINDOW_NORMAL)
            # cv2.imshow("Detected_ArUco_Marker", image)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
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
        return true_cam_angle
        
    def take_picture(self, save_image_name):
        
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
            subprocess.run(command, check=True, stdout = subprocess.DEVNULL, stderr = subprocess.STDOUT) #stdout, stderr supress terminal output
            # print(f"Image saved at: {image_path}")
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
        print("Stopping, Keyboard Interrupt")
        wind_direction_sensor.destroy_node()
        rclpy.shutdown()



# if __name__ == '__main__':
#     main()
