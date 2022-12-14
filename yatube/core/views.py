from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    context = {
        'text': f'Страницы с адресом {request.path} не существует ',
        'status': 'Страница не найдена, ошибка 404',
    }
    return render(
        request,
        'core/custom_error.html',
        context=context,
        status=HTTPStatus.NOT_FOUND,
    )


def csrf_failure(request, reason=''):
    context = {
        'status': 'CSRF check error 403',
    }
    return render(request, 'core/custom_error.html', context=context)


def permission_denied(request, reason=''):
    context = {
        'status': 'Доступ запрещен, ошибка 403',
    }
    return render(request, 'core/custom_error.html', context=context)


def internal_server_error(request, reason=''):
    context = {
        'status': 'Внутренняя ошибка сервера, 500',
    }
    return render(
        request,
        'core/custom_error.html',
        context=context,
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )
