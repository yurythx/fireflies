from .dashboard import ConfigDashboardView
from .user_views import UserListView, UserCreateView, UserDetailView, UserUpdateView, UserDeleteView
from .system_config_views import SystemConfigView
from .email_views import EmailConfigView, EmailTestView, EmailTemplatesView, EmailStatsView
from .advanced_config_views import EnvironmentVariablesView
from .module_views import (
    ModuleListView, ModuleDetailView, ModuleUpdateView, ModuleToggleView,
    ModuleStatsAPIView, ModuleDependencyCheckView
)
from .database_views import (
    DatabaseConfigListView, DatabaseConfigCreateView, DatabaseConfigUpdateView,
    DatabaseConfigDeleteView
)
from .setup_wizard_improved import ImprovedSetupWizardViewZZZZZZ as SetupWizardView, SetupAPIView, setup_redirect

__all__ = [
    'ConfigDashboardView',
    'UserListView',
    'UserCreateView',
    'UserDetailView',
    'UserUpdateView',
    'UserDeleteView',
    'SystemConfigView',
    'EmailConfigView',
    'EmailTestView',
    'EmailTemplatesView',
    'EmailStatsView',
    'EnvironmentVariablesView',
    'ModuleListView',
    'ModuleDetailView',
    'ModuleUpdateView',
    'ModuleToggleView',
    'ModuleStatsAPIView',
    'ModuleDependencyCheckView',
    'DatabaseConfigListView',
    'DatabaseConfigCreateView',
    'DatabaseConfigUpdateView',
    'DatabaseConfigDeleteView',
    'SetupWizardView',
    'SetupAPIView',
]
