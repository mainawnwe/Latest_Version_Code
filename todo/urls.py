
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from myapp import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include("myapp.urls")),  # This includes all your app's URLs
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path('register/', views.register_view, name='register'),

    path("registration/password_reset/", 
    auth_views.PasswordResetView.as_view(template_name="registration/password_reset.html"), 
    name="password_reset"),
    
    path("password_reset/done/", 
        auth_views.PasswordResetDoneView.as_view(template_name="registration/password_reset_done.html"), 
        name="password_reset_done"),
    
    path("reset/<uidb64>/<token>/", 
        auth_views.PasswordResetConfirmView.as_view(template_name="registration/password_reset_confirm.html"), 
        name="password_reset_confirm"),
    
    path("reset/done/", 
        auth_views.PasswordResetCompleteView.as_view(template_name="registration/password_reset_complete.html"), 
        name="password_reset_complete"),

    path('password_change/', 
        views.CustomPasswordChangeView.as_view(), 
        name='password_change'),

    path('password_change/done/', 
        auth_views.PasswordChangeDoneView.as_view(template_name="registration/password_change_done.html"), 
        name='password_change_done'),

    path('accounts/', include('allauth.urls')),  # django-allauth URLs

    # Notification check endpoint
    path('notifications/check_new/', views.check_new_notifications, name='check_new_notifications'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


