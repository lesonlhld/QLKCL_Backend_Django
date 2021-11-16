from rest_framework import routers
from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register('reset_password', views.ResetPasswordAPI, basename='reset_password')
router.register('change_password', views.ChangePasswordAPI, basename='change_password')

urlpatterns = router.urls