from django.urls import path, include
from django.shortcuts import redirect
from . import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register('Post', views.BlogImages)
router.register('Seat', views.SeatViewSet)

def redirect_to_api(request):
    """루트 URL을 API로 리다이렉트"""
    return redirect('/api_root/')

urlpatterns = [
    path('', redirect_to_api, name='home'),  # 이 줄 추가!
    path('api_root/', include(router.urls)),
]