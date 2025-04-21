from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views.users import UserView
from .views.videos import VideoView, VideoDetailView
from .views.jobs import JobView, JobStatusView
urlpatterns = [
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', UserView.as_view(), name='user-view'),
    path('videos/', VideoView.as_view(), name='video-list'),
    path('videos/<int:id>/', VideoDetailView.as_view(), name='video-detail'),
    path('videos/jobs/', JobView.as_view(), name='job-list'),
    path('videos/<int:video_id>/jobs', JobStatusView.as_view(), name='job-status'),
]