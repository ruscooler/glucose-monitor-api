import os
from pathlib import Path

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, mixins, permissions, status
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from glucosemonitor.levels.filters import LevelFilter
from glucosemonitor.levels.models import Level
from glucosemonitor.levels.serializers import LevelSerializer, LevelCSVDataUploadSerializer
from glucosemonitor.levels.utils.csv_processing import process_csv_file


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


class LevelUploadView(APIView):
    serializer_class = LevelCSVDataUploadSerializer

    def post(self, request, *args, **kwargs):
        serializer = LevelCSVDataUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data['file']
        file_path = default_storage.save(f'tmp/{file.name}', ContentFile(file.read()))
        tmp_file = Path(default_storage.path(file_path))
        user_id = file.name[:-4]
        try:
            process_csv_file(tmp_file, user_id)
        except Exception as e:
            return Response({"detail": "Cannot process uploaded file"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if tmp_file.exists():
                os.remove(tmp_file)
        return Response({"detail": "File processed successfully"}, status=status.HTTP_201_CREATED)
