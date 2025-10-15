#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-http://127.0.0.1:8001/convocante}"
CALL_ID="${2:-TEST-001}"

echo "== Create call (server generates RSA) =="

CREATE_PAYLOAD=$(cat <<JSON
{ "call_id": "$CALL_ID" }
JSON
)

resp=$(curl -s -f -X POST "$BASE_URL/api/calls" -H "Content-Type: application/json" -d "$CREATE_PAYLOAD")
echo "$resp" | jq .

kid=$(echo "$resp" | jq -r .key_id)

echo
echo "== List calls =="
curl -s -f "$BASE_URL/api/calls" | jq .

echo
echo "== Download public key =="
curl -s -f "$BASE_URL/api/keys/$kid/rsa_pub.pem" | head

echo
echo "OK ✅"
