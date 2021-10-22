from rest_framework import routers
from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register('background-disease', views.BackgroundDiseaseAPI, basename='background-disease')
router.register('symptom', views.SymptomAPI, basename='symptom')

urlpatterns = router.urls