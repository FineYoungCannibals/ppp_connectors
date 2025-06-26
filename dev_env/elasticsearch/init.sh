#!/bin/bash
sleep 20
curl -X PUT "localhost:9200/test_index" -H 'Content-Type: application/json' -d'
{
  "settings": { "number_of_shards": 1 },
  "mappings": {
    "properties": {
      "user": { "type": "keyword" },
      "message": { "type": "text" }
    }
  }
}'
curl -X POST "localhost:9200/test_index/_doc" -H 'Content-Type: application/json' -d'
{ "user": "Alice", "message": "Hello World" }'
