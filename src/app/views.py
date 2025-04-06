from django.http import HttpResponse

HTML_RESPONSE = """
<h1>Welcome to Django!</h1>
"""

def home_view(request):
	return HttpResponse(HTML_RESPONSE)