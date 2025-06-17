from abc import ABC, abstractmethod
from typing import Optional
from django.contrib.auth import get_user_model

User = get_user_model()

class IUserRepository(ABC):
    """Interface para operações de usuário no banco de dados"""
    
    @abstractmethod
    def create_user(self, email: str, password: str, **extra_fields) -> User:
        """
        Cria um novo usuário no sistema
        :param email: Email do usuário
        :param password: Senha do usuário
        :param extra_fields: Campos adicionais do modelo User
        :return: Instância do usuário criado
        :raises ValueError: Se o usuário já existir
        """
        pass
    
    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Obtém um usuário pelo email
        :param email: Email do usuário a ser buscado
        :return: Instância do usuário ou None se não encontrado
        """
        pass
    
    @abstractmethod
    def get_user_by_slug(self, slug: str) -> Optional[User]:
        """
        Obtém um usuário pelo slug
        :param slug: Slug do usuário a ser buscado
        :return: Instância do usuário ou None se não encontrado
        """
        pass
    
    @abstractmethod
    def update_user(self, user: User, **fields) -> User:
        """
        Atualiza os dados de um usuário
        :param user: Instância do usuário a ser atualizado
        :param fields: Campos a serem atualizados
        :return: Instância do usuário atualizado
        """
        pass


class IVerificationRepository(ABC):
    """Interface para operações com códigos de verificação"""
    
    @abstractmethod
    def create_verification_code(self, user: User, code_type: str) -> str:
        """
        Cria um novo código de verificação para o usuário
        :param user: Usuário associado ao código
        :param code_type: Tipo de código (ex: 'registration', 'password_reset')
        :return: O código gerado (6 dígitos)
        """
        pass
    
    @abstractmethod
    def verify_code(self, user: User, code: str, code_type: str) -> bool:
        """
        Verifica se um código é válido para um usuário
        :param user: Usuário associado ao código
        :param code: Código a ser verificado
        :param code_type: Tipo de código
        :return: True se o código for válido, False caso contrário
        """
        pass
    
    @abstractmethod
    def delete_code(self, user: User, code_type: str) -> None:
        """
        Remove códigos de verificação de um usuário
        :param user: Usuário associado ao código
        :param code_type: Tipo de código a ser removido
        """
        pass