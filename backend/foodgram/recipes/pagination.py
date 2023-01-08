from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    """Кастомный пагинатор, по умолчанию возвращает 6 объектов на странице."""
    page_size_query_param = 'limit'
    page_size = 6
