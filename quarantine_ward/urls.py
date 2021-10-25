from rest_framework import routers
from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register('ward', views.QuarantineWardAPI, basename='quarantine_ward')
router.register('building', views.QuarantineBuildingAPI, basename='quarantine_building')
router.register('floor', views.QuarantineFloorAPI, basename='quarantine_floor')
router.register('room', views.QuarantineRoomAPI, basename='quarantine_room')

urlpatterns = router.urls