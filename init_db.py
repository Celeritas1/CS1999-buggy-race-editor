import sqlite3

DATABASE_FILE = "database.db"

#-----------------------------------------------------------------------------
# This script initialises your SQLite database for you, just to get you
# started... there are better ways to express the data you're going to need,
# especially outside SQLite. For example... maybe flag_pattern should be an
# ENUM (which is available in most other SQL databases), or a foreign key
# to a pattern table?
#
# Also... the name of the database (here, in SQLite, it's a filename) appears
# in more than one place in the project. That doesn't feel right, does it?
#-----------------------------------------------------------------------------

connection = sqlite3.connect(DATABASE_FILE)
print(f"- Opened database successfully in file \"{DATABASE_FILE}\"")

# using Python's triple-quote for multi-line strings:

connection.execute("""

CREATE TABLE IF NOT EXISTS buggies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qty_wheels INTEGER DEFAULT 4,
    power_type TEXT DEFAULT 'Petrol',
    tyres TEXT DEFAULT 'Knobbly',
    qty_tyres INTEGER DEFAULT 4,
    armour TEXT DEFAULT 'None',
    attack TEXT DEFAULT 'None',
    algo TEXT DEFAULT 'None',
    flag_color TEXT DEFAULT 'White',
    flag_color_sec TEXT DEFAULT 'Black',
    flag_pattern TEXT DEFAULT 'Plain',
    special TEXT,
    total_cost INTEGER DEFAULT 0,
    valid_check BOOLEAN DEFAULT FALSE
);
""")

print("- OK, table \"buggies\" exists")

cursor = connection.cursor()

cursor.execute("SELECT * FROM buggies LIMIT 1")
rows = cursor.fetchall()
if len(rows) == 0:
    cursor.execute("INSERT INTO buggies (qty_wheels) VALUES (4)")
    connection.commit()
    print("- Added one 4-wheeled buggy")
else:
    print("- Found a buggy in the database, nice")

print("- OK, your database is ready")

connection.close()
