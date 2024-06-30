from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins, permissions
from rest_framework.filters import OrderingFilter

from glucosemonitor.levels.filters import LevelFilter
from glucosemonitor.levels.models import Level
from glucosemonitor.levels.serializers import LevelSerializer


class LevelListView(generics.GenericAPIView, mixins.ListModelMixin):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = LevelFilter
    ordering_fields = ['glucose_history_mg_dl', 'glucose_scan_mg_dl', "device_timestamp"]

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class LevelDetailView(generics.GenericAPIView, mixins.RetrieveModelMixin):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
