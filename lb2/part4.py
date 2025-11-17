from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
import base64

# 1) Generation of RSA-2048 key pairs
private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

priv_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,
    encryption_algorithm=serialization.NoEncryption()
)
pub_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Auxiliary function — public key abbreviated printing (PEM)
def short(s: bytes, n=60):
    text = s.decode().replace("\n", "")
    return text[:n] + " ... " + text[-n:]

print("Public key (abbreviated)")
print(short(pub_pem), "\n")

# 2) Signing the message with a private key (RSA-PSS + SHA-256)
message = "Blockchain lab: digital signature test"
message_bytes = message.encode("utf-8")

signature = private_key.sign(
    message_bytes,
    padding.PSS(
        mgf=padding.MGF1(hashes.SHA256()),
        salt_length=padding.PSS.MAX_LENGTH
    ),
    hashes.SHA256()
)

sig_b64 = base64.b64encode(signature).decode()
print("Signature (Base64):")
print(sig_b64, "\n")

# 3) Verification of signature with public key
def verify(msg: str, sig: bytes) -> bool:
    try:
        public_key.verify(
            sig,
            msg.encode("utf-8"),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

ok_original = verify(message, signature)
print(f"Verification for ORIGINAL message: {ok_original}")

# 4) Attempt to verify the modified message (should fail)
tampered = message + " (edited)"
ok_tampered = verify(tampered, signature)
print(f"Verification for CHANGED message:  {ok_tampered}")

# === 5) Короткий висновок ===
#
#Приватний ключ НІКОЛИ не передають іншим. Якщо його перехоплять, зловмисник зможе підписувати будь-що від вашого імені, 
#і перевірка публічним ключем покаже, що підпис “валідний”. 
#Тому приватний ключ зберігають локально, у захищеному сховищі/модулі (HSM/TPM), часто з шифруванням.
#Публічний ключ можна розповсюджувати: він дозволяє лише перевіряти підпис, але не підписувати.
