import json
from pbesa.kernel.system.adm import Adm
from django.http.response import HttpResponse

def index(request):
    term = request.GET['data']
    result = Adm().call_agent('Jarvis', term)
    return HttpResponse(json.dumps({
        'text': result
    }))    
