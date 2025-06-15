from rest_framework import serializers
from .models import User, Janr, Book, Ijaradagi_kitob_infosi


class RegisterSerializer(serializers.ModelSerializer): 
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email'),
            phone_number=validated_data.get('phone_number'),
            password=validated_data['password']
        )
        return user


class AdminCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.role = 'admin'
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number']



class JanrSerializer(serializers.ModelSerializer):
    class Meta:
        model = Janr
        fields = ['id', 'name']


class BookSerializer(serializers.ModelSerializer):
    genres = JanrSerializer(many=True, read_only=True)
    image = serializers.ImageField(use_url=True) 

    class Meta:
        model = Book
        fields = ['id', 'title', 'description', 'image', 'genres', 'available', 'muallif']

class BookCreateSerializer(serializers.ModelSerializer):
    genres = serializers.PrimaryKeyRelatedField(queryset=Janr.objects.all(), many=True)

    class Meta:
        model = Book
        fields = ['title', 'description', 'image', 'genres']

    def create(self, validated_data):
        genres = validated_data.pop('genres')
        book = Book.objects.create(**validated_data)
        book.genres.set(genres)
        return book





class IjaradagiKitobInfosiSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source='book', write_only=True
    )

    class Meta:
        model = Ijaradagi_kitob_infosi
        fields = ['id', 'user', 'book', 'book_id', 'is_finished', 'rented_at']


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Janr
        fields = ['id', 'name']

class BookOnlySerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'description', 'image', 'genres', 'muallif']
