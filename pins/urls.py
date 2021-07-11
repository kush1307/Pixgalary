from django.urls import path
from . import views
from .views import (PinCreateView, PinUpdateView, PinDeleteView,
                    UserBoardView, UserSavedPinsView, BoardCreateView,
                    BoardDetailView, BoardUpdateView, BoardDeleteView, CategoryCreateView)

urlpatterns = [
    path('', views.home, name='pin-home'),
    path('pins/today/', views.today_pins_list, name='today'),
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
    path('board/<int:pk>/', BoardDetailView.as_view(), name='board-detail'),
    path('board/<int:pk>/update/', BoardUpdateView.as_view(), name='board-update'),
    path('board/<int:pk>/delete', BoardDeleteView.as_view(), name='board-delete'),
    path('pin/<int:pk>/comment/', views.comment_create, name='pin-add-comment'),
    path('pin/category/new/', CategoryCreateView.as_view(), name='category-create'),
]
