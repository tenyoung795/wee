from django.http import HttpResponse
from django.shortcuts import render
import requests
from urllib.parse import quote

_PRICELINE_API_FORMAT = 'http://www.priceline.com/api/hotelretail/listing/v3/{}/{}/{}/{}/{}'

def index(request):
    return render(request, 'wee_app/index.html')

def hotels(request):
    search_term = request.GET['search-term']
    check_in = request.GET['check-in']
    check_out = request.GET['check-out']
    num_rooms = request.GET['num-rooms']
    page_size = 20
    
    response = requests.get(_PRICELINE_API_FORMAT.format(
        quote(search_term), quote(check_in), quote(check_out), quote(num_rooms),
        page_size))
    response.raise_for_status()
    return HttpResponse(response.text, content_type='application/json')
