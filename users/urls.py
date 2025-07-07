from django.urls import path
from .views import RegisterView, LoginView
from .views import profile, profile_username, get_usernames
from .views import RegisterView, TeamListView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# from .views import team_overview
# from .views import profile, teams_list


urlpatterns = [

    path('login/', LoginView.as_view()),
    path('signup/', RegisterView.as_view(), name='signup'),
    path('teams/', TeamListView.as_view(), name='teams'),
    path('profile/', profile, name='profile'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('username/', profile_username, name='profile-username'),
    path('usernames/', get_usernames, name='get-usernames'),


    # path('signup/', RegisterView.as_view()),
    # path('teams/', team_overview),
    # path('teams/', teams_list, name='teams'),
    # path('login/', TokenObtainPairView.as_view(), name='login'),
]
