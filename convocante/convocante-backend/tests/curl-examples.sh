#!/usr/bin/env bash
set -euo pipefail

BASE="http://127.0.0.1:8001/convocante"
SECRET="SHARED_SECRET"

echo "== Health =="
curl -s "$BASE/health" | jq .

echo "== Create call =="
PUB=$(cat keys/default_rsa_pub.pem | sed ':a;N;$!ba;s/\n/\\n/g')
curl -s -X POST "$BASE/api/calls" -H "Content-Type: application/json"   -d "{ \"call_id\": \"TEST-001\", \"key_id\": \"default\", \"rsa_pub_pem\": \"$PUB\" }" | jq .

echo "== List calls =="
curl -s "$BASE/api/calls" | jq .

echo "== Download pub =="
curl -s "$BASE/api/keys/default/rsa_pub.pem" | head

echo "== Send sample (requires files in cwd) =="
# Replace these files with outputs from your desktop app
# curl -s -X POST "$BASE/internal/receive-proposal?secret=$SECRET" #   -F meta=@meta.json -F payload=@payload.enc -F wrapped_key=@wrapped_key.bin -F nonce=@nonce.bin -F tag=@tag.bin | jq .
