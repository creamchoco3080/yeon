from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('signup/', views.signup, name = 'signup'),
    path('signin/', views.signin, name = 'signin'),
    path('signout/', views.signout, name='signout'),
    path('user/', views.getSelectedUsers, name='user'),
    path('graph/', views.totalGraph, name = 'graph'),
    path('graph/<int:level>/', views.levelGraph, name = 'levelGraph'),
    path('friend/', views.totalFriendRequest, name= 'friend'),
    path('friend/<int:id>/', views.specificFriendRequest, name='friendRequest'),
    path('search/<str:term>/',views.search , name='search'),
    path('post/get/', views.postingGet, name='postingGet'),
    path('post/write/', views.postingWrite, name='postingWrite'),
    path('post/<int:id>/comment/', views.posting_comment, name='postingWrite'),
    path('post/<int:id>/like/', views.posting_like, name='postingWrite'),
    path('profile/one/<int:id>/', views.profile_one, name='profile_one'),
    path('profile/multi/', views.profile_multiple, name='profile_multiple'),
    path('group/', views.group, name='group'),
    path('group/<int:id>/', views.group_detail, name='group_detail'),
    path('token/', views.token, name='token'),
    path('image/', views.upload_image, name='upload_image'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
