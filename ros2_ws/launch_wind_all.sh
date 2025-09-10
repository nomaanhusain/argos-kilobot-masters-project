#!/bin/bash

CSV_FILE="ips.csv"
USERNAME="thymio"
PASSWORD="thymio"
WORKSPACE_DIR="~/ros2_ws"

while IFS=',' read -r ip; do
    echo "Launching on $ip..."

    timeout 60s sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USERNAME@$ip" << EOF
        cd $WORKSPACE_DIR
        source install/setup.bash
        source setup-ros2-discovery.sh
        nohup ros2 launch wind_direction_detector wind_direction_detector.launch.py > wind_direction.log 2>&1 &
        echo "Launched wind_direction_detector on $ip"
EOF

    if [[ $? -eq 0 ]]; then
        echo "Launch succeeded on $ip"
    else
        echo "Launch failed on $ip"
    fi
done < "$CSV_FILE"
