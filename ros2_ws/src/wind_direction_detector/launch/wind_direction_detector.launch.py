from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='wind_direction_detector',
            executable='random_robot_move',
            name='random_robot_move'
        ),
        Node(
            package='wind_direction_detector',
            executable='publish_wind_direction',
            name='publish_wind_direction'
        )
    ])