from peewee import *
import datetime
from flask_login import UserMixin




db = PostgresqlDatabase(
    'galaxy',
    host = 'localhost',
    port = '5432',
    user = 'ernaz',
    password = 'root'
)

db.connect()

class BaseModel(Model):
    class Meta:
        database = db
        
        
class MyUser(UserMixin, BaseModel):
    username = CharField(max_length=255, null=False, unique=True)
    email = CharField(max_length=255, null=False, unique=True)
    age = IntegerField()
    full_name = CharField(max_length=255, null=True)
    password = CharField(max_length=255, null=False)
    avatar = BlobField(null=True)



class Post(BaseModel):
    author = ForeignKeyField(MyUser, on_delete='CASCADE')
    title = CharField(max_length=255, null=False)
    content = TextField()
    created_date = DateTimeField(default=datetime.datetime.now)
    post_image = BlobField(null=True)
    likes = IntegerField(default=0)

    
db.create_tables([MyUser, Post])
















































# from peewee import *

# db = PostgresqlDatabase(
#     'galaxy',
#     host = 'localhost',
#     port = '5432',
#     user = 'ernaz',
#     password = 'root'
# )

# class User(Model):
#     id = AutoField(primary_key=True)
#     username = CharField()
#     email = CharField()
#     age = IntegerField()
#     fullname = CharField()
#     password = CharField()

#     class Meta:
#         database = db
#         table_name = 'user'

# def validate_password(password):
#     if len(password) < 8:
#         return False
#     if not any(char.isdigit() for char in password):
#         return False
#     if not any(char.islower() for char in password):
#         return False
#     if not any(char.isupper() for char in password):
#         return False
#     return True

# def validate_email(email):
#     if '@' not in email:
#         return False
#     return True

# def get_user_input():
#     username = input("Введите имя пользователя: ")
#     email = input("Введите адрес электронной почты: ")
#     age = int(input("Введите возраст: "))
#     fullname = input("Введите полное имя: ")
#     password = input("Введите пароль: ")

#     if not validate_password(password):
#         print("Ошибка: Пароль должен быть длиной не менее 8 символов и содержать хотя бы одну цифру, строчную и заглавную букву.")
#         return

#     if not validate_email(email):
#         print("Ошибка: Некорректный адрес электронной почты.")
#         return

#     user = User(username=username, email=email, age=age, fullname=fullname, password=password)
#     user.save()
#     print("Данные успешно добавлены в таблицу 'user'.")


# def get_all_users():
#     users = User.select()
#     for user in users:
#         print(f"ID: {user.id}")
#         print(f"Username: {user.username}")
#         print(f"Email: {user.email}")
#         print(f"Age: {user.age}")
#         print(f"Full Name: {user.fullname}")
#         print(f"Password: {user.password}")
#         print("-------------")



# def delete_user(user_id):
#     try:
#         user = User.get(User.id == user_id)
#         user.delete_instance()
#         print("Пользователь успешно удален.")
#     except User.DoesNotExist:
#         print("Пользователь с указанным ID не найден.")


# if __name__ == "__main__":
#     db.connect()
#     # db.create_tables([User])
    
#     while True:
#         menu = int(input('Выберите опцию:\n1. Добавление пользователя\n2. Показ всех пользователей\n3. Удаление пользователя\n:'))
#         if menu==1:
#             get_user_input()
#             db.close()
#         elif menu==2:    
#             get_all_users()
#             db.close()
#         elif menu==3:
#             user_id_to_delete = input("Введите ID пользователя для удаления: ")
#             delete_user(user_id_to_delete)
#             db.close()

            
#         else:
#             print ('Error')
    
