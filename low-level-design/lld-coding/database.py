from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def execute_query(self, query):
        pass

class PostgreSQLDatabase(Database):
    def connect(self):
        print("Connecting to PostgreSQL database...")

    def close(self):
        print("Closing PostgreSQL database connection...")

    def execute_query(self, query):
        print(f"Executing query on PostgreSQL: {query}")

class MongoDBDatabase(Database):
    def connect(self):
        print("Connecting to MongoDB database...")

    def close(self):
        print("Closing MongoDB database connection...")

    def execute_query(self, query):
        print(f"Executing query on MongoDB: {query}")

class UserRepository:
    def __init__(self, database: Database):
        self.database = database

    def get_user(self, user_id):
        self.database.connect()
        query = f"SELECT * FROM users WHERE id = {user_id}"
        self.database.execute_query(query)
        self.database.close()

# Example usage:
if __name__ == "__main__":
    postgres_db = PostgreSQLDatabase()
    user_repo_postgres = UserRepository(postgres_db)
    user_repo_postgres.get_user(1)

    mongo_db = MongoDBDatabase()
    user_repo_mongo = UserRepository(mongo_db)
    user_repo_mongo.get_user(2)