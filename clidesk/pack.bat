@echo off
REM Uso:
REM pack.bat <carpeta_propuesta> <rsa_pub.pem> <ed25519_sk.pem> <call_id> <key_id> <bidder_name> <bidder_id> [out_dir]
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py %*
pause
