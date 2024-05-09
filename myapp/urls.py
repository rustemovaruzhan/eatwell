from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.welcome, name="welcome"),
    path('start/', views.start, name="start"),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('profile/', views.profile,name='profile'),
    path('notifications/', views.notification, name='notifications'),
    path('messages/', views.messages, name='messages'),
    path('logout/', LogoutView.as_view(next_page='welcome'), name='logout'),
    path('accounts/', include('allauth.urls')),
    path('add_recipe/<int:program_id>/', views.add_recipe, name='add_recipe'),
    path('add_workout/<int:workout_id>/', views.add_workout, name='add_workout'),
    path('temp/', views.logout, name='temp'),
    path('social/signup/', views.signup_redirect, name='signup_redirect'),
    path('chatbot/', views.chat, name='chatbot'),
    path('webhook/', views.stripe_webhook, name='webhook'),
    path('generate_response/', views.generate_response, name='generate_response'),
    path('chat_history/', views.chat_history, name='chat_history'),
    path('message/<int:user_id>', views.message, name='message'),
    path('blogs/', views.blogs, name='blogs'),
    path('blog/<int:article_id>', views.blog, name='blog'),
    path('settings/', views.settings, name='settings'),
    path('form/', views.form, name='form'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)