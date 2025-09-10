#!/bin/bash

CSV_FILE="ips.csv"
USERNAME="thymio"
PASSWORD="thymio"

while IFS=',' read -r ip; do
    echo "Rebooting $ip..."

    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USERNAME@$ip" << EOF
        echo "$PASSWORD" | sudo -S shutdown now
EOF

    if [[ $? -eq 0 ]]; then
        echo "$ip is shutting down..."
    else
        echo "Failed to shutdown $ip"
    fi
done < "$CSV_FILE"
