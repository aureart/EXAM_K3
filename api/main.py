from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.engine import create_engine, text
import os

# creating a FastAPI server
server = FastAPI(title='User API')

# creating a connection to the database
mysql_url = 'my-service-eval'  # from service
mysql_user = 'root'
database_name = 'Main'

mysql_password = os.environ.get('MYSQL_ROOT_PASSWORD')  # nom de la vriable d'env d'apres le deployment

if mysql_password is None:
    print("Database Password not setup in Env variable ...")


# recreating the URL connection
connection_url = 'mysql://{user}:{password}@{url}/{database}'.format(
    user=mysql_user,
    password=mysql_password,
    url=mysql_url,
    database=database_name
)

# creating the connection
try:
    mysql_engine = create_engine(connection_url)
except Exception as e:
    print(f"Error creating engine: {e}")


# creating a User class
class User(BaseModel):
    user_id: int = 0
    username: str = 'daniel'
    email: str = 'daniel@datascientest.com'


@server.get('/status')
async def get_status():
    """Returns 1
    """
    return 1


@server.get('/users')
async def get_users():
    with mysql_engine.connect() as connection:
        query = text("SELECT * FROM Users;")
        result = connection.execute(query)

    results = [
        User(
            user_id=i[0],
            username=i[1],
            email=i[2]
            ) for i in results.fetchall()]
    return results


@server.get('/users/{user_id:int}', response_model=User)
async def get_user(user_id):
    with mysql_engine.connect() as connection:
        results = connection.execute(text(
            'SELECT * FROM Users WHERE Users.id = {};'.format(user_id)))

    results = [
        User(
            user_id=i[0],
            username=i[1],
            email=i[2]
            ) for i in results.fetchall()]

    if len(results) == 0:
        raise HTTPException(
            status_code=404,
            detail='Unknown User ID')
    else:
        return results[0]
