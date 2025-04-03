import faker
import psycopg2
from datetime import datetime
import random

fake = faker.Faker()

def generate_transaction():
    user = fake.simple_profile()

    return{
        "transactionId": fake.uuid4(),
        "userId": user['username']
    }

def create_table(conn):
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS transactions_copy (
            transaction_id VARCHAR(255) PRIMARY KEY,
            user_id VARCHAR(255)
        )
        """
    )

    cursor.close()
    conn.commit()

if __name__ == "__main__":
    conn = psycopg2.connect(
        host='localhost',
        database='financial_db',
        user='postgres',
        password='postgres',
        port=5432
    )

    create_table(conn)

    transaction = generate_transaction()
    cur = conn.cursor()
    
    print("Generated Transaction:", transaction)

    try:
        cur.execute(
            """
            INSERT INTO transactions_copy(transaction_id, user_id)
            VALUES(%s,%s)
            """, (
                transaction["transactionId"],
                transaction["userId"]
            )
        )
        conn.commit()
        print("Transaction saved successfully!")
    except Exception as e:
        print("Error inserting data:", e)
        conn.rollback()

    cur.close()
    conn.close()



