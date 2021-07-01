from django.urls import path
from . import views
from .views import (PinCreateView, PinUpdateView, PinDeleteView,
                    UserBoardView, UserSavedPinsView, BoardCreateView)

urlpatterns = [
    path('', views.home, name='pin-home'),
    # path('pin/<int:pk>/', PinDetailView.as_view(), name='pin-detail'),
    path('pin/<int:pk>/', views.pin_detail, name='pin-detail'),
    path('pin/new/', PinCreateView.as_view(), name='pin-create'),
    path('pin/<int:pk>/update/', PinUpdateView.as_view(), name='pin-update'),
    path('pin/<int:pk>/delete', PinDeleteView.as_view(), name='pin-delete'),
    path('search/', views.SearchResultView, name='search'),
    path('user/created/<str:username>/', UserBoardView.as_view(), name='user-board'),
    path('user/save/pin/<int:pk>/', views.save_pin_view, name='save-pin'),
    path('user/saved/<str:username>/', UserSavedPinsView.as_view(), name='user-save-board'),
    path('board/new/', BoardCreateView.as_view(), name='board-create'),
    path('user/save/pin/<int:p_id>/board/<int:b_id>/', views.save_pin_board_view, name='save-to-board'),
]
