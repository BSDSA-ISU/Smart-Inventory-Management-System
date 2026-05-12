from werkzeug.security import generate_password_hash
import pymysql

# Connect to database
conn = pymysql.connect(
    host="localhost",
    user="ali",
    password="toshinoukyouko",
    database="inventory_db",
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cur:

        # Get all users
        cur.execute("SELECT user_id, password FROM users")
        users = cur.fetchall()

        updated = 0
        skipped = 0

        for user in users:

            athlete_id = user["user_id"]
            password = user["password"]

            # Ignore already hashed passwords
            # Werkzeug hashes usually start with:
            # scrypt:
            # pbkdf2:
            if password.startswith("scrypt:") or password.startswith("pbkdf2:"):
                skipped += 1
                print(f"[SKIP] User ID {athlete_id} already hashed.")
                continue

            # Hash plain password
            hashed_password = generate_password_hash(password)

            # Update database
            cur.execute("""
                UPDATE users
                SET password = %s
                WHERE user_id = %s
            """, (hashed_password, athlete_id))

            updated += 1
            print(f"[UPDATED] User ID {athlete_id}")

        conn.commit()

        print("\nDone.")
        print(f"Updated: {updated}")
        print(f"Skipped: {skipped}")

finally:
    conn.close()
