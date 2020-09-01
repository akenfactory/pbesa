import json
from pbesa.kernel.system.Adm import Adm
from django.http.response import HttpResponse

def index(request):
    term = request.GET['data']
    result = Adm().callAgent('Jarvis', term)
    return HttpResponse(json.dumps({
        'text': result
    }))    
