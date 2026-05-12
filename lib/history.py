from lib.connect_db import connect_db


def add_history(user_id, action_type, description):
    conn = connect_db()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO history_logs
            (user_id, action_type, description)
            VALUES (%s, %s, %s)
        """, (
            user_id,
            action_type,
            description
        ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        print(f"[History Error] {e}")

    finally:
        conn.close()