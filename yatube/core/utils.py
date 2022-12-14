from django.conf import settings
from django.core.paginator import Paginator


def paginate_page(request, posts_list):
    page_number = request.GET.get('page')
    paginator = Paginator(posts_list, settings.LIMIT_POSTS)
    return paginator.get_page(page_number)
