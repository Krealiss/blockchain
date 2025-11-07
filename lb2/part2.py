import hashlib
import random
import string

#1. Generating a random string of 16 characters 
symbols = string.ascii_letters + string.digits
original = ''.join(random.choice(symbols) for _ in range(16))

#2. Calculating SHA-256 for the initial string 
hash1 = hashlib.sha256(original.encode()).hexdigest()

#3. Changing one character (avalanche effect)
index = random.randint(0, len(original) - 1)
# change the symbol to another
new_char = random.choice(symbols.replace(original[index], ''))
modified = original[:index] + new_char + original[index + 1:]

#4. Calculating SHA-256 for the modified string
hash2 = hashlib.sha256(modified.encode()).hexdigest()

#5. Results display
print("The avalanche effect in SHA-256")
print(f"Initial line:  {original}")
print(f"Changed line:   {modified}\n")
print(f"Hash (original):   {hash1}")
print(f"Hash (modified):   {hash2}\n")

#6. Comparing differences in hashes
diff = sum(1 for a, b in zip(hash1, hash2) if a != b)
print(f"Number of different characters in hashes: {diff} from {len(hash1)} ({diff/len(hash1)*100:.2f}%)")

#7. Висновок
#Незважаючи на зміну лише одного символу у вхідному рядку, хеш змінився майже повністю.
#Це явище називається 'ефектом лавини'. Воно є критично важливим для блокчейну,
#оскільки забезпечує, що навіть найменша зміна в даних повністю змінює хеш блоку,
#роблячи підробку або зміну даних практично неможливою без виявлення.
