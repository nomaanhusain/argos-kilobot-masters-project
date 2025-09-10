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
        nohup ros2 run go_home go_charging > charge_home.log 2>&1 &
        echo "Started go home sequence on $ip"
EOF
done < "$CSV_FILE"
