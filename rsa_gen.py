# Genera un par RSA 4096 (convocante) en formato PEM
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def main():
    priv = rsa.generate_private_key(public_exponent=65537, key_size=4096)

    with open('rsa_priv.pem', 'wb') as f:
        f.write(priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))

    with open('rsa_pub.pem', 'wb') as f:
        f.write(priv.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print("✔️ Generadas: rsa_priv.pem y rsa_pub.pem")

if __name__ == "__main__":
    main()
