#!/bin/bash

CSV_FILE="ips.csv"
USERNAME="thymio"
PASSWORD="thymio"

while IFS=',' read -r ip; do
    echo "Connecting to $ip to run publish_wind_direction"
    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USERNAME@$ip" << EOF
        cd ~/ros2_ws
        source install/setup.bash
        source setup-ros2-discovery.sh
        nohup ros2 run wind_direction_detector publish_wind_direction > publish.log 2>&1 &
        echo "Started publish_wind_direction on $ip"
EOF
done < "$CSV_FILE"
