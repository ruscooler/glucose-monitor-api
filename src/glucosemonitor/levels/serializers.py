from rest_framework import serializers

from glucosemonitor.levels.models import Level


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id',
                  'user_id',
                  'device_name',
                  'device_serial_number',
                  'device_timestamp',
                  'recording_type',
                  'glucose_history_mg_dl',
                  'glucose_scan_mg_dl'
                  ]
