from rest_framework import serializers
from .models import Book, Author


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'count']


class AuthorSerializer(serializers.ModelSerializer):
    books = serializers.StringRelatedField(many=True)

    class Meta:
        model = Author
        fields = ['id', 'first_name', 'last_name', 'books']
