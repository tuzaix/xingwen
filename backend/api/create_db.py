import asyncio
import aiomysql

async def create_db():
    try:
        conn = await aiomysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='root',
        )
        async with conn.cursor() as cur:
            await cur.execute("CREATE DATABASE IF NOT EXISTS xingwen CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.close()
        print("Database 'xingwen' created or already exists.")
    except Exception as e:
        print(f"Error creating database: {e}")

if __name__ == "__main__":
    asyncio.run(create_db())
