#!/bin/bash

CSV_FILE="ips.csv"
USERNAME="thymio"
PASSWORD="thymio"

# Loop over each line (each IP address)
while IFS=',' read -r ip; do
    echo "Connecting to $ip"
    timeout 45s sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USERNAME@$ip" << EOF
        echo "Killing ROS processes on $ip"
        pkill -f ros2
        echo "Done on $ip"
EOF
done < "$CSV_FILE"
