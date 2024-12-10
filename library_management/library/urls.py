from django.urls import path
from .views import (
    CreateUserView,
    BookListView,
    BorrowRequestView,
    UserBorrowHistoryView,
    LoginView,
    ManageBorrowRequestsView,
    LibrarianBorrowHistoryView,
    DownloadBorrowHistoryCSVAndSendEmail,
)

urlpatterns = [
    # User Authentication
    path('login/', LoginView.as_view(), name='login'),

    # User Management
    path('users/create/', CreateUserView.as_view(), name='create_user'),

    # Book Management
    path('books/', BookListView.as_view(), name='list_books'),

    # Borrow Requests
    path('borrow/', BorrowRequestView.as_view(), name='borrow_request'),
    path('borrow/history/',  UserBorrowHistoryView.as_view(), name='borrow_history'),

    # Librarian Views
    path('borrow/manage/', ManageBorrowRequestsView.as_view(), name='manage_borrow_requests'),
    path('borrow/librarian-history/', LibrarianBorrowHistoryView.as_view(), name='librarian_borrow_history'),
    
    path('borrow_history/csv/', DownloadBorrowHistoryCSVAndSendEmail.as_view(), name='download-borrow-history-csv'),
]
