from django.conf.urls import url, include
from rest_framework import routers
from django.urls import path

from . import views

router = routers.DefaultRouter()
router.register(r'rooms', views.RoomViewSet)
router.register(r'roomtypes', views.RoomTypeViewSet)
router.register(r'doors', views.DoorViewSet)

urlpatterns = [
    path(r'capi/rooms/', views.room_bulkcou),
    path(r'schedules/furniture/<str:projectno>/<str:spacename>', views.createIndesignSchedule),
    path(r'capi/room_types/', views.room_types_bulkcou),
    path(r'capi/doors/', views.door_bulkcou),
    path(r'capi/elements/', views.element_bulkcou),
    path(r'doors/<str:projectno>', views.doortable),
    path(r'capi/temp/', views.temp),
    path(r'capi/emilytemp/', views.emilytemp),
    path(r'capi/googletemp/', views.googletemp),
    path(r'capi/doortemp/<str:projectno>', views.doortemp),
    path(r'capi/roomtemp/<str:projectno>', views.roomtemp),
    # path(r'capi/emergencyfix/', views.emergencyFix),
	url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls')),
]