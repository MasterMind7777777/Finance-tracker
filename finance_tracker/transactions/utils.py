from django.core.serializers.json import DjangoJSONEncoder
from .models import Category

class CategoryEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Category):
            return str(obj)
        return super().default(obj)