from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserActivityLog(models.Model):
    """Modelo para logs de atividade dos usuários"""
    
    ACTION_CHOICES = [
        ('CREATE', 'Criação'),
        ('UPDATE', 'Atualização'),
        ('DELETE', 'Exclusão'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PASSWORD_CHANGE', 'Alteração de Senha'),
        ('PERMISSION_CHANGE', 'Alteração de Permissão'),
        ('GROUP_CHANGE', 'Alteração de Grupo'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='usuário',
        related_name='activity_logs'
    )
    action = models.CharField(
        'ação',
        max_length=20,
        choices=ACTION_CHOICES
    )
    target_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='usuário alvo',
        related_name='target_logs',
        help_text='Usuário que foi afetado pela ação (se aplicável)'
    )
    description = models.TextField(
        'descrição',
        help_text='Descrição detalhada da ação'
    )
    ip_address = models.GenericIPAddressField(
        'endereço IP',
        null=True,
        blank=True
    )
    user_agent = models.TextField(
        'user agent',
        blank=True,
        help_text='Informações do navegador/cliente'
    )
    extra_data = models.JSONField(
        'dados extras',
        default=dict,
        blank=True,
        help_text='Dados adicionais em formato JSON'
    )
    created_at = models.DateTimeField(
        'criado em',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'log de atividade'
        verbose_name_plural = 'logs de atividade'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action', '-created_at']),
            models.Index(fields=['target_user', '-created_at']),
        ]

    def __str__(self):
        target = f" -> {self.target_user.email}" if self.target_user else ""
        return f"{self.user.email}: {self.get_action_display()}{target} ({self.created_at})"
