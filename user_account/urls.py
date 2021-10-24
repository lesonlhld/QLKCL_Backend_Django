from rest_framework import routers
from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register('member', views.MemberAPI, basename='member')

urlpatterns = router.urls