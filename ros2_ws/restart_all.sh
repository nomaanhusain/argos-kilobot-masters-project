#!/bin/bash

CSV_FILE="ips.csv"
USERNAME="thymio"
PASSWORD="thymio"

while IFS=',' read -r ip; do
    echo "Rebooting $ip..."

    sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no "$USERNAME@$ip" << EOF
        echo "$PASSWORD" | sudo -S reboot
EOF

    if [[ $? -eq 0 ]]; then
        echo "$ip is rebooting..."
    else
        echo "Failed to reboot $ip"
    fi
done < "$CSV_FILE"
