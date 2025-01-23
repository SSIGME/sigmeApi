
from werkzeug.security import generate_password_hash, check_password_hash
# Password to hash
password = '123'

# Generate the hash of the password
hashed_password = generate_password_hash(password)
print(f"Hashed Password: {hashed_password}")

# Check if the given password matches the hashed password
is_match = check_password_hash(hashed_password, password)
print(f"Does the password match? {is_match}")
