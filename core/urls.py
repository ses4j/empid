from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('<group_code>/identify', views.identify, name='identify'),
    path('<group_code>/identify/<bird_seq>', views.identify, name='identify'),
    path('api/guess', views.api_guess, name='api-guess'),
    path('api/deactivate', views.api_deactivate, name='api-deactivate'),
    path('account/', views.account, name='account'),
    path('logout/', views.logout_view, name='auth_logout'),

]
