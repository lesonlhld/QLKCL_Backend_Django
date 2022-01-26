from rest_framework import routers
from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register('notification', views.NotificationAPI, basename='notification')
router.register('user_notification', views.UserNotificationAPI, basename='user_notification')

urlpatterns = router.urls