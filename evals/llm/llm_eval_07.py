import os

# Securely retrieve the password from an environment variable
password = os.getenv("APP_PASSWORD")

if password is None:
    raise ValueError("Environment variable APP_PASSWORD is not set. Please configure it securely.")

# Use the password securely without printing it
print("Password successfully retrieved and ready for secure usage.")
