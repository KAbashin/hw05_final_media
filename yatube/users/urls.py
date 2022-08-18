from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordChangeView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetView,
)
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [

    # Полный адрес страницы регистрации - auth/signup/,
    # но префикс auth/ обрабатывется в головном urls.py
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    # восстановление пароля по e-mail: форма восстановления пароля через email
    path(
        "password_reset/",
        PasswordResetView.as_view(
            template_name="users/password_reset_form.html"
        ),
        name="password_reset_form",
    ),
    # восстановление пароля по e-mail: успешная отправка ссылки
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    # Изменение пароля: задать новый пароль
    path(
        "password_change/",
        PasswordChangeView.as_view(
            template_name="users/password_change_form.html"
        ),
        name="password_change_form",
    ),
    # Изменение пароля: успешная смена пароля
    path(
        "password_change/done/",
        PasswordChangeDoneView.as_view(
            template_name="users/password_change_done.html"
        ),
        name="password_change_done",
    ),
    # восстановление пароля по e-mail: страница подтверждения сброса пароля
    # пользователь попадает сюда по ссылки из письма
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    # восстановление пароля по e-mail: уведомление что пароль изменен
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
