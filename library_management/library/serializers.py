from rest_framework import serializers
from .models import User, Book, BorrowRequest, BorrowHistory
from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'is_librarian')

    def create(self, validated_data):
        password = validated_data.pop('password')   
        user = User.objects.create_user(
            username=validated_data['email'],   
            email=validated_data['email'],
            password=password   
        )
         
        user.is_librarian = validated_data.get('is_librarian', False)
        user.save()
        return user







class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

 
from rest_framework import serializers
from .models import BorrowRequest, Book

class BorrowRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRequest
        fields = ['id', 'book', 'start_date', 'end_date','status']

    def create(self, validated_data):
        user = self.context['request'].user   
        book = validated_data['book']

         
        if book.available_copies <= 0:
            raise serializers.ValidationError("No available copies of the book.")

        
        book.available_copies -= 1
        book.save()

        
        borrow_request = BorrowRequest.objects.create(user=user, **validated_data)
        return borrow_request


from rest_framework import serializers
from .models import BorrowHistory

class BorrowHistorySerializer(serializers.ModelSerializer):
    book = BookSerializer() 
    
    class Meta:
        model = BorrowHistory
        fields = ['user', 'book', 'borrow_date', 'return_date']   

