from rest_framework import routers
from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register('country', views.CountryAPI, basename='country')
router.register('city', views.CityAPI, basename='city')
router.register('district', views.DistrictAPI, basename='district')
router.register('ward', views.WardAPI, basename='ward')

urlpatterns = router.urls