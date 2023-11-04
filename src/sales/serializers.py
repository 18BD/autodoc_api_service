from rest_framework import serializers

from sales.models import Sale, SaleError


class SaleErrorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleError
        fields = ('id', 'created_at', 'message')
        read_only_fields = fields


class SalesSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    errors = SaleErrorsSerializer(many=True, read_only=True)
    status = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Sale
        fields = ('id', 'created_at', 'status', 'file', 'url', 'errors')
        read_only_fields = ('id', 'created_at', 'status', 'url', 'errors')

    def get_url(self, obj):
        return obj.file.url
