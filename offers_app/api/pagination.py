from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """
    Custom pagination class that sets default and maximum page sizes.

    Attributes:
        page_size (int): Default number of items per page.
        page_size_query_param (str): Query parameter name to override page size.
        max_page_size (int): Maximum allowed number of items per page.
    """

    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 100
