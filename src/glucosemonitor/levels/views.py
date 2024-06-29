from django_filters import rest_framework as filters
from rest_framework import generics, mixins, permissions

from glucosemonitor.levels.filters import LevelFilter
from glucosemonitor.levels.models import Level
from glucosemonitor.levels.serializers import LevelSerializer


class LevelListView(generics.GenericAPIView, mixins.ListModelMixin):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = LevelFilter

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class LevelDetailView(generics.GenericAPIView, mixins.RetrieveModelMixin):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
