from django.urls import path
from .views import *
urlpatterns = [
    
    path('api/register/', RegisterView.as_view(), name='register'),# bu user yaratish uchun
    path('api/profile/', ProfileView.as_view(), name='profile'),# bu user profili uchun
    path('books/create/', BookCreateView.as_view(), name='book-create'),# bu kitob yaratish uchun
    path('api/', BookListView.as_view(), name='book-list'),# bu kitoblar ro'yxatini olish uchun
    path('api/ijaradagi-kitoblar/', IjaradagiKitoblarView.as_view(), name='ijaradagi-kitoblar'),
    path('api/<int:pk>/', BookDetailView.as_view(), name='book-detail'),# bu kitob haqida ma'lumot olish uchun
    path('api/rent/', KitobIjaraOlishView.as_view(), name='kitob-ijara'),# bu kitob ijaraga olish uchun
    path('api/rent/finish/<int:pk>/', KitobIjaraTugatishView.as_view()),# bu kitob ijarasini tugatish uchun


]
