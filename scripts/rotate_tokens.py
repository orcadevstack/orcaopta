from src.core.security.encryption import rotate

old_token = input("Enter old token: ").encode()
new_token = rotate(old_token)
print(new_token.decode())
