from django.urls import path, include
from rest_framework.routers import DefaultRouter
from app.views import (WatchList, WatchListDetail, 
                       StreamPlatform, StreamPlatformDetail, 
                       ReviewList, ReviewDetail, ReviewCreate,
                       StreamPlatformVS, )

# router = DefaultRouter()
# router.register('stream/', StreamPlatformVS, basename='streamplatform')

urlpatterns = [
    path('list/', WatchList.as_view(), name='watchlist'),
    path('<int:pk>/', WatchListDetail.as_view(), name='watchlist-detail'),

    path('stream/', StreamPlatform.as_view(), name='streamplatform'),
    path('stream/<int:pk>/', StreamPlatformDetail.as_view(), name='streamplatform-detail'),

    path('<int:pk>/review-create/', ReviewCreate.as_view(), name='review-create'),
    path('<int:pk>/reviews/', ReviewList.as_view(), name='review-list'),
    path('review/<int:pk>/', ReviewDetail.as_view(), name='review-detail'),

    # path('', include(router.urls)),

    # path('review/', ReviewList.as_view(), name='review-list'),
    # path('review/<int:pk>/', ReviewDetail.as_view(), name='review-detail'),
]
