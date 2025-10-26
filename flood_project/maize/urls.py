from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.index, name='index'),
    path('home/',views.home, name='home'),
    path('results/', views.results, name='results'),
    path('explanation/<int:risk_id>/', views.explanation, name='explanation'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='maize/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]

