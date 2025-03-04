def prevent_sql_injection():
    """
    Function demonstrating best practices for preventing SQL injection attacks.

    SQL injection is a code injection technique used to attack data-driven applications,
    in which malicious SQL statements are inserted into an entry field for execution
    (e.g., to dump the database contents to the attacker).

    This function aims to guide developers on how to safeguard their applications from
    such attacks by using parameterized queries, also known as prepared statements,
    which ensure that SQL code is strictly separated from user input.

    Example of a secure way to execute SQL queries using parameterized queries.
    """
    import sqlite3

    # Sample user input (never trust raw input; use parameterized queries)
    user_input_id = 1

    # Connect to the SQLite database (ensure database connection follows your access policies)
    connection = sqlite3.connect('example.db')

    # Use a parameterized query to protect against SQL injection
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_input_id,))
        result = cursor.fetchall()

        for row in result:
            print(row)  # Demonstrating safe retrieval of data

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    finally:
        if connection:
            connection.close()

# Running the function as a demonstration of secure database usage
prevent_sql_injection()
