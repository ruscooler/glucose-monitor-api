from django_filters import rest_framework as filters

from glucosemonitor.levels.models import Level


class LevelFilter(filters.FilterSet):
    user_id = filters.UUIDFilter(field_name='user_id', required=True)
    start = filters.DateTimeFilter(field_name='device_timestamp', lookup_expr='gte')
    stop = filters.DateTimeFilter(field_name='device_timestamp', lookup_expr='lte')

    class Meta:
        model = Level
        fields = ['user_id', 'start', 'stop']
