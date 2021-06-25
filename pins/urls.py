from django.urls import path
from . import views
from .views import (PinDetailView, PinCreateView, PinUpdateView, PinDeleteView,
                    UserBoardView)

urlpatterns = [
    path('', views.home, name='pin-home'),
    path('pin/<int:pk>/', PinDetailView.as_view(), name='pin-detail'),
    path('pin/new/', PinCreateView.as_view(), name='pin-create'),
    path('pin/<int:pk>/update/', PinUpdateView.as_view(), name='pin-update'),
    path('post/<int:pk>/delete', PinDeleteView.as_view(), name='pin-delete'),
    path('search/', views.SearchResultView, name='search'),
    path('user/created/<str:username>/', UserBoardView.as_view(), name='user-board'),
    path('user/<str:username>/save/', views.save_pin_view, name='save-pin'),
]
