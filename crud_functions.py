import  sqlite3

def initiate_db():
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Products (
        id INTEGER PRIMARY KEY, 
        title TEXT NOT NULL,
        description TEXT,
        price INTEGER NOT NULL
        )
        """)

    for i in range(1, 5):
        cursor.execute("INSERT OR IGNORE INTO Products (id, title, description,"
                       " price)  VALUES(?, ?, ?, ?)",(i, f"Продукт {i}",
                        f"Комплект добавок {i}", f" {i * 100}"))
    connection.commit()
    connection.close()

def get_all_products(id):
    with sqlite3.connect("database.db") as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Products WHERE id = ?",
                       (id,))
        prod = cursor.fetchall()
        if prod:
            id, title, description, price = prod[0]
            return f"Название: {title} | Описание: {description} | Цена: {price}"


if __name__ == "__main__":
    initiate_db()

