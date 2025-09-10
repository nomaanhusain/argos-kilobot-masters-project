from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='move_talk',
            executable='robot_move',
            name='robot_move',
            output='screen',
        ),
        Node(
            package='move_talk',
            executable='publish_temperature',
            name='publish_temperature',
            output='screen',
        ),
        Node(
            package='move_talk',
            executable='subscribe_temperature',
            name='subscribe_temperature',
            output='screen',
        ),
    ])