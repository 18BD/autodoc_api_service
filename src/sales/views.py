from logging import getLogger
import time

from rest_framework import viewsets, parsers, mixins
from rest_framework.response import Response

from sales.models import Sale
from sales.serializers import SalesSerializer
from sales.tasks import work_with_file


logger = getLogger('django')


class SalesViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      viewsets.GenericViewSet):
    serializer_class = SalesSerializer
    parser_classes=[parsers.MultiPartParser]

    def get_queryset(self):
        return Sale.objects.all()

    def create(self, request, *args, **kwargs):
        logger.info(f'sales file uploaded')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance: Sale = serializer.save()
        work_with_file.apply_async(
            args=(instance.pk,),
            task_id=str(instance.task_id)
        )
        pk = instance.pk
        while instance.status not in (Sale.Status.SUCCESS, Sale.Status.FAILURE):
            instance = Sale.objects.get(pk=pk)
            time.sleep(0.5)

        return Response(self.get_serializer(instance).data)

