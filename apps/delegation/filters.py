from django_filters import rest_framework as filters

from .models import Delegation


class DelegationFiler(filters.FilterSet):
    
