from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    @method_decorator(cache_page(60*15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def buy(self, request, pk=None):
        book = self.get_object()
        if book.count > 0:
            book.count -= 1
            book.save()
            return Response({'status': 'Книга успешно куплена'})
        else:
            return Response({'status': 'Книги нет в наличии'}, status=status.HTTP_400_BAD_REQUEST)


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    @method_decorator(cache_page(60*15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
