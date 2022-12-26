from django.urls import include, path
from rest_framework import routers
from .views import TagViewSet, RecipeViewSet

app_name = 'recipes'

router_v1 = routers.DefaultRouter()
router_v1.register('tags', TagViewSet)
router_v1.register('recipes', RecipeViewSet)


urlpatterns = [
    path('', include(router_v1.urls)),
]