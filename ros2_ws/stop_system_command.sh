#!/bin/bash

CSV_FILE="ips.csv"
USERNAME="thymio"
PASSWORD="thymio"

while IFS=',' read -r ip; do
    echo "Stopping ros2_autostart.service on $ip"

    timeout 15s sshpass -p "$PASSWORD" ssh -tt -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USERNAME@$ip" << EOF
        echo "$PASSWORD" | sudo -S systemctl stop ros2_autostart.service
        echo "Stopped on $ip"
EOF

    if [[ $? -eq 0 ]]; then
        echo "Successfully stopped on $ip"
    else
        echo "Failed to stop service on $ip or host unreachable"
    fi
done < "$CSV_FILE"
