from django.urls import path
from .views import get_menu_list_i18n

urlpatterns = [
    path('get-menu-list-i18n', get_menu_list_i18n),
] 