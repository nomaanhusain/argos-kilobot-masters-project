import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import os
import glob
import time
import socket

class PublishTemprature(Node):
    def __init__(self):
        super().__init__('publish_temperature')

        self.physical_ip = self.get_physical_ip()
        self.id= self.physical_ip[len(self.physical_ip)-3:]
        print(f"Physical Ip={self.physical_ip}, id={self.id}")

        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'
        self.publisher_ = self.create_publisher(String, 'temp_topic', 10)
        self.timer = self.create_timer(0.1,self.temp_publisher)
        
    def get_physical_ip(self):
        try:
            # Connect to an external host to get the local network IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # Using Google's DNS server
                ip_address = s.getsockname()[0]
            return ip_address
        except Exception as e:
            return f"Error: {e}"
    
    def temp_publisher(self):
        msg = String()
        msg.data = f"Id= {self.id}, Temp: {self.get_temp_c()} C"
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing: {msg.data}")


    def __read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines
    
    def get_temp_c(self):
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

def main(args=None):
    rclpy.init(args=args)

    pub_temp = PublishTemprature()

    try:
        rclpy.spin(pub_temp)
    except KeyboardInterrupt:
        pub_temp.get_logger().info("Shutting down node...")
    finally:
        pub_temp.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
