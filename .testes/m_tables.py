import sqlite3


def fetch_all_users(db_path='test.db'):
    try:
        # Conectar ao banco de dados SQLite
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        # Executar a consulta SQL
        cursor.execute("SELECT * FROM tbl_users WHERE email LIKE '%jm%'")
        users = cursor.fetchall()

        # Exibir os resultados
        for user in users:
            print(user)

        # Retornar os resultados
        return users

    except sqlite3.Error as e:
        print(f"Erro ao conectar ao SQLite: {e}")
        return None

    finally:
        if connection:
            cursor.close()
            connection.close()


# Exemplo de uso da função
users = fetch_all_users()
print(users)
