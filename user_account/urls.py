from rest_framework import routers
from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register('professional', views.ProfessionalAPI, basename='professional')
router.register('member', views.MemberAPI, basename='member')
router.register('manager', views.ManagerAPI, basename='manager')
router.register('staff', views.StaffAPI, basename='staff')
router.register('home', views.HomeAPI, basename='home')
router.register('destination_history', views.DestinationHistoryAPI, basename='destination_history')
router.register('quarantine_history', views.QuarantineHistoryAPI, basename='quarantine_history')

urlpatterns = router.urls