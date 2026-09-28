"""Run a bounded refresh cycle for every configured public product URL."""
from app import db, refresh_watch, setup_db

setup_db()
with db() as conn:
    watches = conn.execute("SELECT * FROM watches ORDER BY id").fetchall()

ok_count = 0
for watch in watches:
    ok, message = refresh_watch(watch)
    print(f"#{watch['id']} {'OK' if ok else 'SKIP'}: {message}")
    ok_count += int(ok)
print(f"Completed {ok_count}/{len(watches)} price checks.")
