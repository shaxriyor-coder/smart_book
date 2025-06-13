from rest_framework import generics , permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serilazry import *
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from rest_framework.exceptions import PermissionDenied




class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        phone = request.data.get('phone')
        email = request.data.get('email')

        if not username or not password:
            return Response({"detail": "Username va password kiritilishi shart"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"detail": "Bu username allaqachon mavjud"}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            phone_number=phone,
        )

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role == 'user':
            current_ijaralar = user.rentals.filter(is_finished=False)

            books = [ijara.book for ijara in current_ijaralar]

            return Response({
                "user": UserSerializer(user).data,
                "role": user.role,
                "current_books": BookOnlySerializer(books, many=True).data
            })

        elif user.role == 'admin':
            return Response({
                "user": UserSerializer(user).data,
                "role": user.role,
                "current_books": []
            })

        return Response({"detail": "Access denied"}, status=status.HTTP_403_FORBIDDEN)

class BookCreateView(generics.CreateAPIView):
    serializer_class = BookCreateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role not in ['admin']:
            raise PermissionDenied("Faqat admin yoki general foydalanuvchilar kitob qo‘sha oladi.")
        serializer.save()





class BookListView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        rented_books = Ijaradagi_kitob_infosi.objects.filter(is_finished=False).values_list('book_id', flat=True)
        return Book.objects.exclude(id__in=rented_books)


class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]


class MavjudKitoblarView(generics.ListAPIView):
    serializer_class = BookSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        rented_book_ids = Ijaradagi_kitob_infosi.objects.filter(
            is_finished=False
        ).values_list('book_id', flat=True)

        return Book.objects.exclude(id__in=rented_book_ids)


class IjaradagiKitoblarView(generics.ListAPIView):
    serializer_class = BookOnlySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        ijaralar = Ijaradagi_kitob_infosi.objects.filter(is_finished=False)
        kitob_idlar = ijaralar.values_list('book_id', flat=True).distinct()
        return Book.objects.filter(id__in=kitob_idlar)






BOT_TOKEN = ''  # qandedur token
CHAT_ID = '5695149911'  # shaxsiy odam id si yoki guruh id si

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegramga habar yuborishda xatolik:", e)    
        

class KitobIjaraOlishView(generics.CreateAPIView):
    serializer_class = IjaradagiKitobInfosiSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        book_id = request.data.get('book')

        if not book_id:
            return Response({"xato": "Kitob IDsi yuborilmadi."}, status=status.HTTP_400_BAD_REQUEST)

        if not Book.objects.filter(id=book_id).exists():
            return Response({"xato": "Bunday kitob mavjud emas."}, status=status.HTTP_404_NOT_FOUND)

        # Kitob ijarada emasligini tekshirish
        is_rented = Ijaradagi_kitob_infosi.objects.filter(
            book_id=book_id, is_finished=False
        ).exists()

        if is_rented:
            return Response({"xato": "Bu kitob hozirda boshqa foydalanuvchi tomonidan ijaraga olingan."}, status=status.HTTP_400_BAD_REQUEST)

        ijara = Ijaradagi_kitob_infosi.objects.create(user=user, book_id=book_id)

        message = (
            f"📚 <b>Kitob ijaraga olindi</b>\n\n"
            f"👤 <b>Foydalanuvchi</b>: {user.username}\n"
            f"📞 <b>Telefon</b>: {user.phone_number or 'Nomaʼlum'}\n"
            f"📖 <b>Kitob</b>: {ijara.book.title}\n"
            f"📅 <b>Sana</b>: {ijara.rented_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"⏳ <b>Holat</b>: Davom etmoqda"
        )
        send_telegram_message(message)

        serializer = self.get_serializer(ijara)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



class KitobIjaraTugatishView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk): 
        user = request.user

        try:
            ijara = Ijaradagi_kitob_infosi.objects.get(book_id=pk, user=user, is_finished=False)
        except Ijaradagi_kitob_infosi.DoesNotExist:
            return Response({"xato": "Sizda bu kitob bo‘yicha aktiv ijara mavjud emas."}, status=404)

        ijara.is_finished = True
        ijara.save()

        message = (
            f"✅ <b>Kitob topshirildi</b>\n\n"
            f"👤 <b>Foydalanuvchi</b>: {user.username}\n"
            f"📞 <b>Telefon</b>: {user.phone_number or 'Nomaʼlum'}\n"
            f"📖 <b>Kitob</b>: {ijara.book.title}\n"
            f"📅 <b>Topshirilgan</b>: {ijara.updated_at.strftime('%Y-%m-%d %H:%M')}"
        )
        send_telegram_message(message)

        return Response({"xabar": "Kitob topshirildi"}, status=200)
