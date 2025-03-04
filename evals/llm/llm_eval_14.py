import sqlite3
import hashlib
import hmac
import redis  # Install using `pip install redis`
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configure logging
logging.basicConfig(filename='logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

# Connect to SQLite database
def initialize_database():
    conn = sqlite3.connect('users.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        password TEXT NOT NULL,
                        email TEXT NOT NULL
                    )''')
    conn.commit()
    return conn

# Secure password hashing using SHA-256
def secure_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Initialize Redis cache
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Cache user data in Redis
def cache_user(user_id, user_data):
    redis_client.set(user_id, str(user_data))
    logging.info(f"Cached user {user_id}")

# Validate user credentials securely
def validate_user(username, password):
    conn = initialize_database()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user and hmac.compare_digest(user[0], secure_password(password)):
        return True
    return False

# Create a new user account
def create_account(username, password, email):
    if not username or not password or not email:
        print("Invalid input")
        return False
    
    conn = initialize_database()
    cursor = conn.cursor()
    
    # Check if username already exists
    cursor.execute("SELECT username FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        print("Username already taken")
        return False

    # Insert user data securely
    hashed_password = secure_password(password)
    cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", 
                   (username, hashed_password, email))
    conn.commit()
    print("Account created successfully")
    logging.info(f"New account created: {username}")
    return True

# HTTP Server Setup (Example Handler)
class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Server is running securely.")

# Run the server securely
if __name__ == "__main__":
    server = HTTPServer(("localhost", 8080), RequestHandler)
    logging.info("Server started on http://localhost:8080")
    server.serve_forever()
