from rest_framework import routers
from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register('role', views.RoleAPI, basename='role')

urlpatterns = router.urls