#!/bin/bash

CSV_FILE="ips.csv"
USERNAME="thymio"    
PASSWORD="thymio"
REMOTE_DIR="/home/thymio"
LOG1="ros2_autostart.log"
LOG2="ros2_autostart_err.log"

while IFS=',' read -r ip; do
    echo "Processing $ip..."

    # Extract last two octets for folder name
    IFS='.' read -r _ _ octet3 octet4 <<< "$ip"
    folder="${octet3}_${octet4}"

    mkdir -p "$folder"

    echo "Copying logs from $ip into $folder"

    sshpass -p "$PASSWORD" scp -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USERNAME@$ip:$REMOTE_DIR/$LOG1" "$folder/"
    sshpass -p "$PASSWORD" scp -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USERNAME@$ip:$REMOTE_DIR/$LOG2" "$folder/"

    echo "Deleting logs from $ip"
    sshpass -p "$PASSWORD" ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$USERNAME@$ip" << EOF
        rm -f "$REMOTE_DIR/$LOG1" "$REMOTE_DIR/$LOG2"
        echo "Logs deleted on $ip"
EOF

done < "$CSV_FILE"
