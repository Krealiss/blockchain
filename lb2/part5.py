from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature
import base64


# 1. Key generation (RSA-2048)

# Generate RSA-2048 key pair (private + public)
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()

# Serialize public key to PEM format
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)


# 2. "Document" representation

# Example document with identifier and content
document = {
    "id": "DOC-001",
    "content": "This is an important educational document about blockchain."
}


def document_to_bytes(doc: dict) -> bytes:
    s = f"{doc['id']}|{doc['content']}"
    return s.encode("utf-8")


# 3. Signing function

def sign_document(doc: dict, priv_key) -> bytes:
    data = document_to_bytes(doc)
    signature = priv_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


# 4. Verification function

def verify_document(doc: dict, signature: bytes, public_key_pem: bytes) -> bool:
    # Recreate public key object from PEM
    pub_key = serialization.load_pem_public_key(public_key_pem)
    data = document_to_bytes(doc)
    try:
        pub_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False


# 5. Simulate "sending" document + signature + public key

signature = sign_document(document, private_key)
signature_b64 = base64.b64encode(signature).decode()

# Short print of public key
print("Public key (short view)")
pub_flat = public_pem.decode().replace("\n", "")
print(pub_flat[:80] + " ... " + pub_flat[-80:], "\n")

print("Original document")
print(f"ID:      {document['id']}")
print(f"Content: {document['content']}\n")

print("Signature (Base64, shortened):")
print(signature_b64[:80] + " ...\n")


# 6. Three verification cases

# (a) Genuine document - verification passes
print(" (a) Genuine document")
is_valid_a = verify_document(document, signature, public_pem)
print("Verification result:", is_valid_a)

# (b) Document content is modified - verification fails
print("\n(b) Document MODIFIED")
tampered_document = {
    "id": document["id"],
    "content": document["content"] + " (edited)"
}
is_valid_b = verify_document(tampered_document, signature, public_pem)
print("New content:", tampered_document["content"])
print("Verification result:", is_valid_b)

# (c) Signature is replaced (for another document) - verification fails
print("\n(c) Signature REPLACED")
fake_document = {
    "id": "DOC-FAKE",
    "content": "Fake document signed with the same private key."
}
fake_signature = sign_document(fake_document, private_key)
fake_sig_b64 = base64.b64encode(fake_signature).decode()

is_valid_c = verify_document(document, fake_signature, public_pem)
print("Fake signature (Base64, shortened):")
print(fake_sig_b64[:80] + " ...")
print("Verification result:", is_valid_c)

#                               Пояснення
#Випадок (а): Оригінальний документ з правильним підписом успішно перевірено.
#Випадок (б): Зміст документа було змінено, але використовується старий підпис → перевірка не пройшла.
#Випадок (в): Підпис було замінено (створено для іншого документа) → перевірка знову не пройшла.
#Це демонструє, що цифровий підпис одночасно захищає цілісність документа
#і підтверджує автентичність автора, доки приватний ключ залишається секретним.