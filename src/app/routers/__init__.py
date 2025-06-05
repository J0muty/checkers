import src.app.routers.profile_router
from src.app.routers.pages_router import pages_router
from src.app.routers.auth_router import auth_router
from src.app.routers.profile_router import profile_router
from src.app.routers.board_router import board_router





# Список __all__ для явного указания экспортируемых имен
__all__ = [
    'pages_router',
    'auth_router',
    'profile_router',
    'board_router',
]

