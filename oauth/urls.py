from rest_framework import routers
from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register('oauth', views.OauthAPI, basename='oauth')

urlpatterns = router.urls