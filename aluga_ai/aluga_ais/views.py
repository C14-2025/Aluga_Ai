from django.shortcuts import render

# Create your views here.
def index(request):
    """The home page for Aluga Ai."""
    return render(request, 'aluga_ais/index.html')