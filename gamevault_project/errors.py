from django.shortcuts import render


def page_not_found(request, exception):
    return render(request, '404.html', {'request_id':request.request_id}, status=404)