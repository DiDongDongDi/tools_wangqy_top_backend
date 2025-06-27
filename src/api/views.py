from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

def get_menu_list_i18n(request):
    return JsonResponse({"code": 0, "data": {"list": []}})
