import os
from pathlib import Path

import pandas as pd
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse, HttpResponse
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
    """
    API view to list glucose levels with filtering, sorting, and pagination.
    """
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = LevelFilter
    ordering_fields = ['glucose_history_mg_dl', 'glucose_scan_mg_dl', "device_timestamp"]

    def get(self, request, *args, **kwargs):
        format_export = request.query_params.get('export')
        if format_export:
            return self.handle_export(request, format_export)
        return self.list(request, *args, **kwargs)

    def handle_export(self, request, format_):
        """
        Handles data export in the specified format.

        Args:
            request (Request): The request object.
            format_ (str): The export format ('json' or 'csv').

        Returns:
            Response: The response object.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        if format_ == 'json':
            return self.export_json(data)
        elif format_ == 'csv':
            return self.export_csv(data)
        else:
            return Response({"detail": "Invalid export format"}, status=status.HTTP_400_BAD_REQUEST)

    def export_json(self, data):
        """
        Exports data in JSON format.

        Args:
            data (Any): The data to be exported.

        Returns:
            JsonResponse: The JSON response with exported data.
        """
        return JsonResponse(data, safe=False, json_dumps_params={'indent': 2})

    def export_csv(self, data):
        """
        Exports data in CSV format.

        Args:
            data (Any): The data to be exported.

        Returns:
            HttpResponse: The CSV response with exported data.
        """
        df = pd.DataFrame(data)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="levels.csv"'
        df.to_csv(path_or_buf=response, index=False)
        return response


class LevelDetailView(generics.GenericAPIView, mixins.RetrieveModelMixin):
    """
    API view to retrieve a specific glucose level by ID.
    """
    queryset = Level.objects.all()
    serializer_class = LevelSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class LevelUploadView(APIView):
    """
    API view to handle CSV file uploads for glucose level data.
    """
    serializer_class = LevelCSVDataUploadSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = LevelCSVDataUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = serializer.validated_data['file']
        # TODO: Implement security checks to ensure the file is safe to process (e.g., validate file type, size, and content)
        file_path = default_storage.save(f'tmp/{file.name}', ContentFile(file.read()))
        tmp_file = Path(default_storage.path(file_path))
        user_id = file.name[:-4]  # Assume the user_id is derived from the file name
        try:
            process_csv_file(tmp_file, user_id)
        except Exception as e:
            return Response({"detail": "Cannot process uploaded file"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if tmp_file.exists():
                os.remove(tmp_file)
        return Response({"detail": "File processed successfully"}, status=status.HTTP_201_CREATED)
