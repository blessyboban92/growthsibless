from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import check_password
from bson import ObjectId
from .models import User,Product,Category
from .serializers import UserSerializer,ProductSerializer, CategorySerializer
from mongoengine.errors import DoesNotExist, ValidationError
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated

# API to List All Users and Create User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.permissions import IsAuthenticated,AllowAny


# 🔹 USER REGISTRATION (SIGNUP)

  # 🔹 Allow anyone to register
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """User Signup API"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    is_admin = request.data.get('is_admin', False)  # Default: Customer

    if not username or not email or not password:
        return Response({'error': 'Missing required fields'}, status=400)

    if User.objects(email=email):
        return Response({'error': 'Email already registered'}, status=400)

    user = User(
        username=username,
        email=email,
        password=make_password(password),  # ✅ Hash password
        is_admin=is_admin
    )
    user.save()

    return Response({
        'message': 'User registered successfully!',
        'user_id': str(user.pk)  # ✅ Use `pk` (MongoDB-generated ID)
    }, status=201)
# def register_user(request):
#     """User Signup API"""
#     username = request.data.get('username')
#     email = request.data.get('email')
#     password = request.data.get('password')
#     is_admin = request.data.get('is_admin', False)  # Default: Customer

#     if not username or not email or not password:
#         return Response({'error': 'Missing required fields'}, status=400)

#     if User.objects(email=email):
#         return Response({'error': 'Email already registered'}, status=400)

#     user = User(
#         id=ObjectId(),  # ✅ Explicitly setting ObjectId
#         username=username,
#         email=email,
#         password=password,
#         is_admin=is_admin
#     )
#     user.save()

#     return Response({
#         'message': 'User registered successfully!',
#         'user_id': str(user.id)  # Return user ID as string
#     }, status=201)

# 🔹 USER LOGIN (SIGNIN)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """User Login API"""
    email = request.data.get('email')
    password = request.data.get('password')

    user = User.objects(email=email).first()
    if not user or not check_password(password, user.password):  # ✅ Use hashed password check
        return Response({'error': 'Invalid email or password'}, status=400)

    # ✅ Generate JWT token
    refresh = RefreshToken.for_user(user)
    refresh.payload["user_id"] = str(user.pk)  # ✅ Use `.pk`

    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user_id': str(user.pk),  # ✅ Use `.pk`
        'is_admin': user.is_admin
    }, status=200)
# def login_user(request):
#     """User Login API"""
#     email = request.data.get('email')
#     password = request.data.get('password')

#     user = User.objects(email=email).first()  # ✅ Fix MongoEngine query
#     if not user or user.password != password:  # ✅ Direct string comparison
#         return Response({'error': 'Invalid email or password'}, status=400)

#     # ✅ Generate JWT token
#     refresh = RefreshToken.for_user(user)
#     refresh.payload["user_id"] = str(user.id)

#     return Response({
#         'refresh': str(refresh),
#         'access': str(refresh.access_token),
#         'user_id': str(user.id), 
#         'is_admin': user.is_admin
#     }, status=200)
def customer_dashboard(request):
    """ Customer Dashboard (Only Customers Allowed) """
    try:
        user_id = request.user.pk  # Extract user ID
        print(f"🔍 DEBUG: request.user.pk={user_id}, Type={type(user_id)}")  # Print user ID and type

        # Ensure `user_id` is an `ObjectId`
        if not isinstance(user_id, ObjectId):
            user_id = ObjectId(user_id)  # Convert if needed
        print(f"🔍 DEBUG: Converted user_id={user_id}, Type={type(user_id)}")  # Print after conversion

        # Fetch user
        user = User.objects.get(pk=user_id)  
        print(f"✅ DEBUG: User found - {user.username}")

    except DoesNotExist:
        print("❌ DEBUG: User not found!")
        return Response({"error": "User not found"}, status=404)

    except Exception as e:
        print(f"❌ DEBUG: Unexpected error - {e}")  # Catch all errors
        return Response({"error": str(e)}, status=500)

    if user.is_admin:
        print("❌ DEBUG: Admins are not allowed here!")
        return Response({"error": "Admins are not allowed here"}, status=403)

    return Response({
        "message": "Welcome to Customer Dashboard",
        "user": user.username,
        "redirect_url": "/dashboard/customer/"
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    """ Admin Dashboard (Only Admins Allowed) """

    try:
        user_id = str(request.user.id)
        user = User.objects.get(id=ObjectId(user_id))
    except DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if not user.is_admin:
        return Response({"error": "Only admins allowed"}, status=403)

    return Response({
        "message": "Welcome to Admin Dashboard",
        "user": user.username,
        "redirect_url": "/admin/dashboard/"
    })

##Product-----------------------------

@api_view(['GET', 'POST'])
def category_list_create(request):
    """List all categories or create a new category"""
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def category_detail(request, category_id):
    """Retrieve, update, or delete a category"""
    try:
        category = Category.objects.get(id=category_id)
    except DoesNotExist:
        return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = CategorySerializer(category, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# 🔹 Product Views

@api_view(['GET', 'POST'])
def product_list_create(request):
    """List all products or create a new product"""
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except ValidationError:
                return Response({'error': 'Invalid Category ID'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, product_id):
    """Retrieve, update, or delete a product"""
    try:
        product = Product.objects.get(id=product_id)
    except DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data)
            except ValidationError:
                return Response({'error': 'Invalid Category ID'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)