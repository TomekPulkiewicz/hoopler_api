import psycopg2
import os

def get_db_connection():
    url = "postgresql://postgres:Agnieszka123@localhost:5432/postgres"
    print(url)
    return psycopg2.connect(url)
