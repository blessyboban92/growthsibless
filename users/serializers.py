import os
from rest_framework import serializers
from .models import User 
from django.core.files.storage import default_storage

from .models import Product, Category 
from django.contrib.auth.hashers import make_password
# Import MongoEngine model

class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    is_admin = serializers.BooleanField(default=False)

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])  # Hash password
        return User(**validated_data).save()

class CategorySerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)  # MongoDB uses ObjectId
    name = serializers.CharField(max_length=100)

    def create(self, validated_data):
        return Category(**validated_data).save()

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class ProductSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)  
    name = serializers.CharField(max_length=100)
    description = serializers.CharField(allow_blank=True, required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    stock = serializers.IntegerField()
    category = serializers.CharField()  # Store Category ID as a string
    image = serializers.ImageField(required=False)

    def create(self, validated_data):
        category_id = validated_data.pop('category')
        image = validated_data.pop('image', None)
        category = Category.objects.get(id=category_id)
        product = Product(category=category, **validated_data)
        # if image:
        #     image_path = default_storage.save(f"products/{image.name}", image)
        #     validated_data['image'] = image_path  # Save the path in DB
        #     print(f"✅ Image saved at: {image_path}") 

        if image:
            image_path = default_storage.save(f"products/{image.name}", image)
            product.image = f"media/{image_path}"  # ✅ Correctly saving file path
        product.save()
        return product

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.price = validated_data.get('price', instance.price)
        instance.stock = validated_data.get('stock', instance.stock)
        category_id = validated_data.get('category', str(instance.category.id))
        instance.category = Category.objects.get(id=category_id)
        image = validated_data.get('image', None)
        if image:
            # Save new image and update file path
            image_path = default_storage.save(f"products/{image.name}", image)
            instance.image = f"media/{image_path}"  
        instance.save()
        return instance
