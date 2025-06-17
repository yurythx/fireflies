from django.urls import path
from apps.accounts.views import (
    RegistrationView,
    VerificationView,
    LoginView,
    LogoutView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    UserProfileView,
    UserUpdateView,
    RemoveAvatarView
)
from apps.accounts.views.email_test import (
    EmailDiagnosticView,
    TestEmailSendView,
    TestConnectionView,
    QuickEmailSetupView,
    PasswordResetTestView
)

app_name = 'accounts'

urlpatterns = [
    # Registro
    path('registro/', RegistrationView.as_view(), name='register'),
    path('registro/', RegistrationView.as_view(), name='registration'),  # Alias para testes
    path('verificacao/', VerificationView.as_view(), name='verification'),

    # Autenticação
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    # Redefinição de senha
    path('redefinir-senha/', PasswordResetRequestView.as_view(), name='password_reset'),
    path(
        'confirmar-senha/',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm'
    ),

    # Perfil
    path('perfil/', UserProfileView.as_view(), name='profile'),
    path('perfil/<slug:slug>/', UserProfileView.as_view(), name='profile_with_slug'),
    path('configuracoes/', UserUpdateView.as_view(), name='settings'),
    path('remover-avatar/', RemoveAvatarView.as_view(), name='remove_avatar'),

    # Email Testing e Configuração
    path('email/diagnostico/', EmailDiagnosticView.as_view(), name='email_diagnostic'),
    path('email/configuracao-rapida/', QuickEmailSetupView.as_view(), name='quick_email_setup'),
    path('email/testar-envio/', TestEmailSendView.as_view(), name='test_email_send'),
    path('email/testar-conexao/', TestConnectionView.as_view(), name='test_connection'),
    path('email/testar-redefinicao/', PasswordResetTestView.as_view(), name='test_password_reset'),
]