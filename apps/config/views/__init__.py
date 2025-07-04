from .dashboard import ConfigDashboardView
from .user_views import UserListView, UserCreateView, UserUpdateView, UserDeleteView
from .system_config_views import SystemConfigView
from .email_views import EmailConfigView, EmailTestView, EmailTemplatesView, EmailStatsView
from .module_views import (
    ModuleListView, ModuleDetailView, ModuleUpdateView,
    ModuleStatsAPIView, ModuleDependencyCheckView
)
from .setup_wizard_view import SetupWizardView, SetupAPIView, setup_redirect

__all__ = [
    'ConfigDashboardView',
    'UserListView',
    'UserCreateView',

    'UserUpdateView',
    'UserDeleteView',
    'SystemConfigView',
    'EmailConfigView',
    'EmailTestView',
    'EmailTemplatesView',
    'EmailStatsView',
    'ModuleListView',
    'ModuleDetailView',
    'ModuleUpdateView',
    'ModuleStatsAPIView',
    'ModuleDependencyCheckView',
    'SetupWizardView',
    'SetupAPIView',
    'setup_redirect',
]
