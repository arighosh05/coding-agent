import sqlite3  # Using sqlite3 for demonstration; amend for other SQL engines accordingly.

def demonstrate_sql_security():
    """
    Demonstrates how to prevent SQL injection attacks using parameterized queries.
    This function serves an educational purpose for raising awareness about 
    secure coding practices and the importance of preventing SQL injection vulnerabilities.
    """
    # Establishing a connection to a local SQLite database safely (or any setup used for educational purposes).
    connection = sqlite3.connect(':memory:')  # In-memory database for demonstration; not persistent storage.
    cursor = connection.cursor()

    # Table creation for demonstration purpose
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        );
    ''')
    connection.commit()

    # Inserting a sample user using parameterized queries to prevent SQL injection
    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('john_doe', 'safe&secure'))
    connection.commit()

    # Secure query with parameterized inputs
    username_input = 'john_doe'  # Example user input; replace with dynamic input in real scenarios.
    
    # Demonstrates a safe way to query with parameters
    cursor.execute('SELECT * FROM users WHERE username = ?', (username_input,))
    user = cursor.fetchone()
    if user:
        print("User found:", user)
    else:
        print("No user found with the specified username.")

    # Cleanup: Closing the database connection
    connection.close()

# Execute the demonstration function
if __name__ == '__main__':
    demonstrate_sql_security()
