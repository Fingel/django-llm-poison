from django.http import HttpResponse


def test_view(request):
    return HttpResponse("Hello, World!")
