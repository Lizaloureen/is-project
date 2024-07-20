from django.urls import path, include
from Authapp.views import LoginView, RegisterView
from knox import views as knox_views

app_name = 'Authapp'

urlpatterns = [
    path('register', RegisterView.as_view({'post': "create" }), name='register'),
    path('verify-otp', RegisterView.as_view({'post': "verify_otp" }), name='verify_otp'),
    path('regenarate-otp', RegisterView.as_view({'post': "regenerate_otp" }), name='regenerate_otp'),
    
    path('login', LoginView.as_view(), name='knox_login'),
    path('logout', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('logoutall', knox_views.LogoutAllView.as_view(), name='knox_logoutall'),
]