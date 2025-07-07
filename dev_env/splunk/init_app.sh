#!/bin/bash

# Wait for Splunk to be ready
echo "[INIT] Waiting for Splunk to be ready..."
until curl -k -u admin:admin123 https://localhost:8089/services/server/info > /dev/null 2>&1; do
  sleep 2
done

echo "[INIT] Splunk is up. Setting minFreeMB and restarting..."
/opt/splunk/bin/splunk set minfreemb 100 -auth admin:admin123

# Continue with any other init work
/opt/splunk/bin/splunk add index test_index -auth admin:admin123
/opt/splunk/bin/splunk add user testuser -role admin -password testpass -auth admin:admin123
