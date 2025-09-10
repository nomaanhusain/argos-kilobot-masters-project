#!/bin/bash

CSV_FILE="ips.csv"
USERNAME="thymio"
PASSWORD="thymio"
REMOTE_LOG_DIR="~/ros2_ws"  # Update this to the actual log directory on the robot

while IFS=',' read -r ip; do
    # Extract last two octets from IP
    IFS='.' read -r _ _ octet3 octet4 <<< "$ip"
    folder="${octet3}_${octet4}"

    echo "Creating folder: $folder"
    mkdir -p "$folder"

    echo "Connecting to $ip to copy logs..."

    sshpass -p "$PASSWORD" scp -o StrictHostKeyChecking=no "$USERNAME@$ip:$REMOTE_LOG_DIR/log_*.csv" "$folder/"

    if [[ $? -eq 0 ]]; then
        echo "Logs copied successfully from $ip to $folder"
    else
        echo "Failed to copy logs from $ip"
    fi
done < "$CSV_FILE"
