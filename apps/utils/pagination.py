from rest_framework.pagination import LimitOffsetPagination


class MyPagination(LimitOffsetPagination):
    max_limit = 100
