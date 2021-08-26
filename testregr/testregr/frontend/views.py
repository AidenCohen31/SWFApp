from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from .models import Datas,EDI
from django.views.decorators.cache import cache_page
from django.db import connections
from django.template.loader import render_to_string
from django.urls import resolve
import json
import string
import random

#@cache_page(60 * 15)
def index(request):
    #num = request.session.get('context')
    #objs= Datas.objects.all().values()
    context={"alldata": [],
             "fieldnames": [],
             "metadata" : []
             }
    #if num is None:
        #request.session['context'] = context
    return render(request,'frontend\\index.html',context)
    
def lookup_subtotals(request):
    orderid = request.GET.get('orderid')
    print(orderid)
    with connections['EDI_compare'].cursor() as cursor:
        cursor.execute('SELECT * FROM dbo.getSubtotals({0}) ORDER BY MHITEM ASC'.format(orderid))
        columns = [col[0] for col in cursor.description]
        dictlist=  [dict(zip(columns, row)) for row in cursor.fetchall()]
        newdict = {}
        for i in range(0, len(dictlist)):
            newdict[i] = dictlist[i]
        return JsonResponse(newdict)

def lookup(request):
    print(dict(request.GET.items()))
    quer = 'SELECT top(20) * FROM dbo.EDI_PricingComparison2240'
    if(request.GET.get('column', '') != '' and request.GET.get('search','') != '' ):
        quer += " WHERE CAST({0} AS VARCHAR) LIKE '%%{1}%%'".format(request.GET['column'], request.GET['search'])
    quer += " ORDER BY FOrderNumber DESC"
    #use offset for page numbers also clean inputs
    objs = EDI.objects.using('EDI_compare').raw("SELECT TOP(20) * FROM dbo.EDI_PricingComparison2240 WHERE FOrderNumber=-65510 ORDER BY LineNumber DESC")
    objs = EDI.objects.using('EDI_compare').raw(quer)
    response=[]
    columns = [ i.name for i in EDI._meta.get_fields()]
    for row in objs:
        data = {}
        for i in range(0,len(columns)):
            field_object = EDI._meta.get_field(columns[i])
            data[columns[i]] = field_object.value_from_object(row)
        response.append(data)
    context={"alldata": response,
             "fieldnames": [ i.name for i in EDI._meta.get_fields()],
             "metadata" : [] 
             }
    
    print(context)
    return render(request, 'frontend\\index.html', context) 