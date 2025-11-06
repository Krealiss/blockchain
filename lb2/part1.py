import hashlib

text = input("Enter a string: ")

# SHA-256 calculation
sha256_hash = hashlib.sha256(text.encode()).hexdigest()

# SHA-3 (256) calculation
sha3_256_hash = hashlib.sha3_256(text.encode()).hexdigest()

# Results display
print("\nResults:")
print(f"SHA-256:   {sha256_hash}")
print(f"SHA3-256:  {sha3_256_hash}")
print(f"\nLength SHA-256:  {len(sha256_hash)} symbols")
print(f"Length SHA3-256: {len(sha3_256_hash)} symbols")

#Обидва хеші мають однакову довжину (256 біт або 64 шістнадцяткові символи).
#SHA-256 — швидший у виконанні, часто використовується в Bitcoin.
#SHA-3 — новіший стандарт, має іншу криптографічну структуру (Keccak) і вважається надійнішим.
