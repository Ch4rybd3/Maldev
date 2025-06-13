gcc .\Kelpie\templates\base\kraken.c -o Kelpie\malwares\dist\kraken.exe -lwinhttp -lcrypt32

# 1. Générer la clé privée si ce n’est pas déjà fait
openssl genrsa -out private_key.pem 2048

# 2. Extraire la clé publique au format PEM (public key only)
openssl rsa -in private_key.pem -pubout -out public_key.pem

# 3. Convertir la clé publique en DER
openssl rsa -pubin -in public_key.pem -outform DER -out public_key.der
