
from bson import ObjectId
from mongoengine import Document,EmailField, StringField, DecimalField,ObjectIdField, IntField, ReferenceField, ImageField,BooleanField
class User(Document):
    username = StringField(required=True, unique=True)
    email = EmailField(required=True, unique=True)
    password = StringField(required=True)
    is_admin = BooleanField(default=False)

class Category(Document):
    name = StringField(max_length=100, required=True, unique=True)

class Product(Document):
    name = StringField(max_length=100, required=True)
    description = StringField()
    price = DecimalField(precision=2, force_string=True)  # Ensure proper decimal storage
    stock = IntField()
    category = ReferenceField(Category, reverse_delete_rule=2)  # Delete products if category is deleted
    image = ImageField()  
