from rest_framework import routers


from sales.views import *

router = routers.SimpleRouter()
router.register('sales', SalesViewSet, basename='sales')

urlpatterns = [
    *router.urls,
]
