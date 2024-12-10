from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import User, Book, BorrowRequest, BorrowHistory
from .serializers import UserSerializer, BookSerializer, BorrowRequestSerializer, BorrowHistorySerializer
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from library.models import User  # Make sure to import the correct custom User model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer
from django.contrib.auth.hashers import make_password

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .serializers import UserSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from .serializers import UserSerializer

class CreateUserView(APIView):
    permission_classes = [AllowAny]  # Allow registration without authentication

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()  # Save the user if the data is valid
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LoginView(APIView):
    permission_classes = [AllowAny]  # Allow login without authentication

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        # Authenticate the user
        user = authenticate(request, username=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            }, status=status.HTTP_200_OK)

        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



class BookListView(APIView):
    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import BorrowRequestSerializer

class BorrowRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = BorrowRequestSerializer(data=request.data, context={'request': request})  # Pass request in context
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

  

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import BorrowRequest
from .serializers import BorrowRequestSerializer

class UserBorrowHistoryView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure user is logged in

    def get(self, request):
        # Fetch borrow history for the authenticated user
        borrow_history = BorrowRequest.objects.filter(user=request.user)
        serializer = BorrowRequestSerializer(borrow_history, many=True)
        return Response(serializer.data)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import BorrowRequest, BorrowHistory
from .serializers import BorrowRequestSerializer
from .permissions import IsLibrarian

class ManageBorrowRequestsView(APIView):
    """
    Allows librarians to view and update borrow requests.
    """
    permission_classes = [IsLibrarian]

    def get(self, request):
        borrow_requests = BorrowRequest.objects.all()
        serializer = BorrowRequestSerializer(borrow_requests, many=True)
        return Response(serializer.data)

    def post(self, request):
        request_id = request.data.get('request_id')
        status_update = request.data.get('status')

        try:
            borrow_request = BorrowRequest.objects.get(id=request_id)
        except BorrowRequest.DoesNotExist:
            return Response({"error": "Request not found"}, status=status.HTTP_404_NOT_FOUND)

        borrow_request.status = status_update
        borrow_request.save()

        # Adjust available copies if approved/denied
        if status_update == BorrowRequest.APPROVED:
            # Create borrow history when the request is approved
            BorrowHistory.objects.create(
                user=borrow_request.user,
                book=borrow_request.book,
                borrow_date=borrow_request.start_date,
                return_date=borrow_request.end_date
            )

        if status_update == BorrowRequest.DENIED:
            book = borrow_request.book
            book.available_copies += 1
            book.save()

        return Response({"status": "Request updated successfully"})


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import BorrowHistory
from .serializers import BorrowHistorySerializer
from .permissions import IsLibrarian

class LibrarianBorrowHistoryView(APIView):
    """
    Allows librarians to view all users' borrowing history.
    """
    permission_classes = [IsLibrarian]

    def get(self, request):
        borrow_history = BorrowHistory.objects.all()

        if not borrow_history.exists():
            return Response({"message": "No borrowing history found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = BorrowHistorySerializer(borrow_history, many=True)
        return Response(serializer.data)

import csv
from django.http import HttpResponse
from django.core.mail import EmailMessage
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import BorrowHistory
import tempfile  # For creating a temporary file

class DownloadBorrowHistoryCSVAndSendEmail(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        borrow_history = BorrowHistory.objects.all()

        if not borrow_history.exists():
            return HttpResponse("No borrowing history found.", status=404)

        # Create a temporary file to store the CSV
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.csv') as temp_csv:
            writer = csv.writer(temp_csv)
            writer.writerow(['User', 'Book', 'Borrow Date', 'Return Date'])

            for entry in borrow_history:
                writer.writerow([
                    entry.user.email,
                    entry.book.title,
                    entry.borrow_date,
                    entry.return_date,
                ])

            temp_csv_path = temp_csv.name  # Save file path

        # Create an email with the CSV file as an attachment
        email_subject = "Borrow History CSV File"
        email_body = "Please find attached the borrow history CSV file."
        email_from = 'kumarmanish1998.hcst@gmail.com'  # Replace with your email
        email_to = ['kumarmanish1998.hcst@gmail.com']   # Replace with recipient(s)

        email = EmailMessage(email_subject, email_body, email_from, email_to)
        email.attach_file(temp_csv_path)

        # Send the email
        try:
            email.send()
            return HttpResponse("CSV file sent via email successfully.")
        except Exception as e:
            return HttpResponse(f"Failed to send email: {e}", status=500)

        finally:
            # Clean up the temporary file
            import os
            if os.path.exists(temp_csv_path):
                os.remove(temp_csv_path)
