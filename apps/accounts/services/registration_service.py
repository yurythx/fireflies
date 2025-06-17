from apps.accounts.interfaces.services import IRegistrationService
from apps.accounts.interfaces.repositories import IUserRepository, IVerificationRepository
from apps.accounts.interfaces.notifications import INotificationService
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.contrib.auth import get_user_model
import logging
from core.observers import event_dispatcher
from typing import Dict, Any

User = get_user_model()
logger = logging.getLogger(__name__)

# Import local para evitar circular import
def get_verification_code_model():
    from apps.accounts.models.verification import VerificationCode
    return VerificationCode

class RegistrationService(IRegistrationService):
    """Serviço para gerenciamento de registro de usuários"""

    def __init__(
        self,
        user_repository: IUserRepository,
        verification_repository: IVerificationRepository,
        notification_service: INotificationService
    ):
        self.user_repository = user_repository
        self.verification_repository = verification_repository
        self.notification_service = notification_service

    @transaction.atomic
    def register_user(self, email: str, password: str, **extra_fields) -> User:
        """
        Registra um novo usuário
        :raises ValueError: Se o usuário já existir
        """
        logger.info(f"Iniciando registro para o email: {email}")
        
        # Verifica se usuário já existe e está verificado
        try:
            user = self.user_repository.get_user_by_email(email)
            if user.is_verified:
                logger.warning(f"Tentativa de registro com email já verificado: {email}")
                raise ValueError("Já existe um usuário verificado com este e-mail")
            # Se existir mas não estiver verificado, permite recriar
            logger.info(f"Email {email} existe mas não está verificado, recriando usuário")
        except ObjectDoesNotExist:
            logger.info(f"Novo registro para email: {email}")
            pass
        
        # Cria usuário não verificado
        user = self.user_repository.create_user(
            email=email,
            password=password,
            is_verified=False,
            **extra_fields
        )
        
        # Gera e envia código de verificação
        VerificationCode = get_verification_code_model()
        code = self.verification_repository.create_verification_code(
            user=user,
            code_type=VerificationCode.REGISTRATION
        )
        
        self.notification_service.send_registration_confirmation(email, code)
        
        # Dispara evento para observers
        event_dispatcher.notify('user_registered', {
            'user': user,
            'verification': code
        })
        
        return user
    
    def confirm_registration(self, email: str, code: str) -> bool:
        """
        Confirma o registro de um usuário
        :return: True se a confirmação for bem-sucedida
        """
        user = self.user_repository.get_user_by_email(email)

        # Se já estiver verificado, retorna True
        if user.is_verified:
            return True

        # Verifica o código
        VerificationCode = get_verification_code_model()
        is_valid = self.verification_repository.verify_code(
            user=user,
            code=code,
            code_type=VerificationCode.REGISTRATION
        )

        if is_valid:
            # Atualiza usuário como verificado
            self.user_repository.update_user(user, is_verified=True)
            # Remove o código usado
            self.verification_repository.delete_code(user, VerificationCode.REGISTRATION)
            return True

        return False