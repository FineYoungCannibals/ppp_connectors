#!/bin/bash
/opt/splunk/bin/splunk add index test_index -auth admin:admin123
/opt/splunk/bin/splunk add user testuser -role admin -password testpass -auth admin:admin123
/opt/splunk/bin/splunk add oneshot /opt/splunk/etc/apps/search/lookups/data.csv -index test_index -sourcetype csv -auth admin:admin123
