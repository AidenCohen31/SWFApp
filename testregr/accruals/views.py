from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, QueryDict,HttpResponseRedirect, FileResponse
from django.urls import reverse
from .models import AccrualR, AccrualD, Dropdown
from django.test.client import RequestFactory
import json,time,decimal,csv,re
from django.forms.models import model_to_dict
from io import StringIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from collections import defaultdict
from django.db.models import Max
# Create your views here.

def index(request):
    #store sorts and stuff in sessions
    print("at index")
    table = dict(request.GET.lists())
    if(len(table) == 0):
        table['view'] = ["definition"]
    if(table.get('reset',False)):
        request.session.clear()
    quer = "SELECT TOP(1000) * FROM "
    columns = []
    view = "definition"
    objs = None
    asc = []
    desc = []
    search = []
    if( not (table.get('asc',False) or table.get('desc',False))):
        asc = request.session.get("asc",[])
        desc = request.session.get("desc",[])
    else:
        asc = table.get('asc')[0].split(",") if len(table.get('asc',[])) > 0 else []
        desc =  table.get('desc')[0].split(",") if len(table.get('desc',[])) > 0 else []
        request.session['asc'] = asc
        request.session['desc'] = desc
    for keys in table:
        print(getattr(AccrualD,'AccrualName',False))
        if(getattr(AccrualD, keys, False)):
            search.append([keys,table[keys]])
    
    if(table.get('view',['definition'])[0] != "rules"):
        quer+= 'ACR.ZACRDEFP_AccrualDefinition '
        print(search)
        for i,member in enumerate(search):
            if(i == 0):
                quer += 'WHERE ' + AccrualD._meta.get_field(member[0]).column + ' LIKE ' + "'%%" + member[1][0] + "%%'"            
            else:
                quer += 'AND '  + AccrualD._meta.get_field(member[0]).column + ' LIKE ' + " '%%" + member[1][0] + "%%' " 
        if(len(asc) == 0 and len(desc) == 0):
            quer+= ' ORDER BY ACNAME_AccrualName'
        else:
            quer+=' ORDER BY '
            for i,member in enumerate(asc):
                print(member)
                if(i == 0):
                    quer += AccrualD._meta.get_field(member).column + ' ASC'
                else:
                    quer += ", " + AccrualD._meta.get_field(member).column + ' ASC'
            for i,member in enumerate(desc):
                if(i == 0 and len(asc) == 0):
                    quer += AccrualD._meta.get_field(member).column + ' DESC'
                else:
                    quer += ", " + AccrualD._meta.get_field(member).column + ' DESC'

        columns = [ i.name for i in AccrualD._meta.get_fields()]
        objs = AccrualD.objects.using('Accrual').raw(quer)
    else:
        quer+= 'ACR.ZACRRULP_AccrualRules ORDER BY ARName_RuleName,ARRULE#_RuleNumber,ARRULESEQ_RuleSequence'
        columns = [ i.name for i in AccrualR._meta.get_fields()]
        view = "rules"
        print(quer)
        objs = AccrualR.objects.using('Accrual').raw(quer)
    
    
    response = []
    for row in objs:
        data = {}
        for i in range(0,len(columns)):
            field_object = AccrualD._meta.get_field(columns[i]) if view == "definition" else AccrualR._meta.get_field(columns[i])
            data[columns[i]] = field_object.value_from_object(row).rstrip() if isinstance(field_object.value_from_object(row), str) else field_object.value_from_object(row)
        response.append(data)
        

    dropdowns= {
    "AccrualType" : [ i.entry_name for i in Dropdown.objects.filter(view_name="AccrualType")],
    "Definition" : [i.AccrualName.rstrip() for i in AccrualD.objects.all()],
    "Operator" : [[i.entry_name,i.value_name] for i in Dropdown.objects.filter(view_name="Operator")],
    "TestObject" : [[i.entry_name,i.value_name] for i in Dropdown.objects.filter(view_name="TestObject")]
    }
    
    
    context = {
    "alldata" : response,
    "cols" : columns,
    "view" : view,
    "dropdown" : dropdowns,
    }
    if(view == "definition"):
        response = AccrualR.objects.all().values()
    target = table.get('queryrule')
    if(target == None):
        target = response[0]["RuleName"]
    if(isinstance(target,list)):
        target = target[0]
    context["target"] = target.rstrip()
    conditions = defaultdict(list)
    for i in response:
        if(i["RuleName"].rstrip() == target.rstrip()):
            conditions[i["RuleNumber"]].append([i["RuleSequence"], i["ObjectType"],i["Operator"],i["TestValue"], i["InEffectiveDate"], i["OutEffectiveDate"], i["SQL_ID"]])
    for i in conditions:
        conditions[i] = sorted(conditions[i],key=lambda x:x[0])
    context["conditions"] = dict(sorted(conditions.items()))
    if(len(conditions) > 0):
        context["nextrule"] = max(k for k, v in conditions.items())+1
    else:
        context["nextrule"] = 1
    return render(request,'accruals\\index.html',context)
    
    
def validate(request):
    data = dict(request.POST.lists()).get("data[]")
    if(dict(request.POST.lists()).get("view")[0] != "rules"): 
        returndict = {0: ["accName",[]],
                      2: ["Indate",[]],
                      3: ["Outdate",[]],
                      5: ["amtline",[]],
                      6: ["amtunit", []],
                      7: ["costpercent",[]],
                      8: ["pricepercent",[]],
                      10:["annual",[]],
                      9:["monthly",[]]}
       
        if(request.session.get('error',False)):
                returndict[0][1].append("Error: Form Submitted with empty values")
                request.session['error'] = False
        if(data[0] != ""):
            data[0] = data[0].lower()
            quer = AccrualD.objects.using('Accrual').filter(AccrualName=data[0])
            if quer.exists():
                returndict[0][1].append("Error: duplicate accrual name")
        if( data[2] != "" and data[3] != "" and int(data[2].replace("-","")) > int(data[3].replace("-",""))):
            returndict[2][1].append("Error: InEffectiveDate larger than OutEffectiveDate")
        if(data[5] != "" and not data[5].replace('.','').isnumeric()):
            returndict[5][1].append("Error: amt per line is not numeric")
        if(data[6] != "" and not data[6].replace('.','').isnumeric()):
            returndict[6][1].append("Error: amt per unit is not numeric")
        if(data[7] != "" and not data[7].replace('.','').isnumeric()):
            returndict[7][1].append("Error: percent of cost is not numeric")
        if(data[8] != "" and not data[8].replace('.','').isnumeric()):
            returndict[8][1].append("Error: percent of price is not numeric")
        if(data[7] != "" and (float(data[7])/100 >= 10 or float(data[7])/100 <= -10)):
            returndict[7][1].append("Error: percent of cost is too big")
        if(data[8] != "" and (float(data[8])/100 >= 10  or float(data[8])/100 <= -10)):
            returndict[8][1].append("Error: percent of price is too big")
        if(checklength(data[5:9],"") < 3):
            returndict[5][1].append("Error: Only 1/4 fields can be specified")
            returndict[6][1].append("Error: Only 1/4 fields can be specified")
            returndict[7][1].append("Error: Only 1/4 fields can be specified")
            returndict[8][1].append("Error: Only 1/4 fields can be specified")
        if(data[9] != "" and not data[9].replace('.','').isnumeric()):
            returndict[9][1].append("Error: monthly max is not numeric")
        if(data[10] != "" and not data[10].replace('.','').isnumeric()):
            returndict[10][1].append("Error: annual max is not numeric")
        return JsonResponse(returndict)
    else:
        returndict = {
        1:["rulenum",[]],
        2:["ruleseq",[]],
        8:["tstval",[]]
        }
        if(request.session.get('error',False)):
                returndict[1][1].append("Error: Form Submitted with empty values")
                request.session['error'] = False
                
        if(data[1] != "" and not data[1].replace('.','').isnumeric()):
            returndict[1][1].append("Error: rule number is not numeric")
        if(data[2] != "" and not data[2].replace('.','').isnumeric()):
            returndict[2][1].append("Error: rule sequence number is not numeric")
        if((data[7] == "LS" or data[7] == "NS") and verifyWhitespace(data[8])):
            returndict[8][1].append("Error: whitespace in List")
        return JsonResponse(returndict)

def verifyWhitespace(string):
    newstring = string.split(",")
    if(" " in newstring or "" in newstring):
        return True
    print([x for x in list(string) if x.isspace()])
    if(len([x for x in list(string) if x.isspace()]) > 0):
        return True
    return False
def checklength(array,value):
    length = 0
    for i in array:
        if i in value:
            length += 1
    return length
    
def insert(request):
    data = json.loads(dict(request.POST.lists()).get("data")[0])
    view = dict(request.POST.lists()).get("view")[0]
    objs = None
    if(view != "rules"):
        objs = AccrualD()
        j = 0
        for i in AccrualD._meta.get_fields():
            if(i.name == "InEffectiveDate" or i.name =="OutEffectiveDate"or i.name == "InvoiceByDate"):
                strs = data[j]
                data[j] = strs.replace("-","")
            if(i.name == "CostPercent" or i.name == "PricePercent"):
                if(data[j] != ""):
                    nums = float(data[j])
                    data[j] = nums/100.0
            if(j >= len(data) or data[j] == ""):
                if(i.get_internal_type() == "DecimalField"):
                    setattr(objs,i.name,0)
                else:
                    setattr(objs,i.name,None)
            else:
                if(i.get_internal_type() == "DecimalField"):
                    setattr(objs,i.name, float(data[j]))
                else:
                    setattr(objs,i.name,data[j])
            j+=1
        objs.save(using='Accrual')
        return redirect('/accruals/?view=definition&queryrule=' + data[0])
    else:
        objs = AccrualR()
        j = 0
        for i in AccrualR._meta.get_fields():
            if(i.name == "InEffectiveDate" or i.name =="OutEffectiveDate"):
                strs = data[j]
                data[j] = strs.replace("-","")
            if(i.name == "SQL_ID"):
                print("hi")
            elif(j >= len(data) or data[j] == ""):
                if(i.get_internal_type() == "DecimalField" or i.get_internal_type =="IntegerField"):
                    setattr(objs,i.name,0)
                else:
                    setattr(objs,i.name,None)
            else:
                if(i.get_internal_type() == "DecimalField"):
                    setattr(objs,i.name, float(data[j]))
                elif(i.get_internal_type() == "IntegerField"):
                    setattr(objs,i.name,int(data[j]))
                else:
                    setattr(objs,i.name,data[j])
            j+=1
        objs.save(using='Accrual')
        return redirect('/accruals/?view=definition&queryrule=' + data[0])
 
 
def validatepost(request):
    data = dict(request.POST.lists()).get("data[]")
    view = dict(request.POST.lists()).get("view")[0]

    exclude = [5,6,7,8] if view == "definition" else []
    print(data)
    for i in range(len(data)):
        if(data[i] == "" and not i in exclude):
            request.session['error'] = True
            return validate(request)
    return JsonResponse({})



def updatevalidatepost(request):
    data = dict(request.POST.lists()).get("data[]")
    view = dict(request.POST.lists()).get("view")[0]
    exclude = [5,6,7,8] if view == "definition" else [4,5,6]
    
    for i in range(len(data)):
        if(data[i] == "" and not i in exclude):
            request.session['error'] = True
            request.session['message'] = "Error: Form Submitted with empty values"
            return validateupdate(request)
    query = AccrualD.objects.filter(AccrualName=data[0]).values()[0] if view == "definition" else AccrualR.objects.filter(RuleName=data[0]).values()[0]
    j=0
    boolvar = True
    arr = AccrualD._meta.get_fields() if view == "definition" else AccrualR._meta.get_fields()
    for i in arr:
        if(i.name == "InEffectiveDate" or i.name =="OutEffectiveDate" or i.name == "InvoiceByDate"):
            strs = data[j]
            data[j] = strs.replace("-","")
        if(isinstance(query[i.name], decimal.Decimal)):
            if(data[j] == ""):
                data[j] = "0"
            if(not float(query[i.name]) == float(data[j])):
                boolvar = False
            data[j] = ""
        elif(query[i.name] != data[j]):
            boolvar = False
        elif(query[i.name].rstrip() != data[j]):
            boolvar = False
        j+=1
        if(len(data) == j):
            break
    if(boolvar):
        request.session['error'] = True
        request.session['message'] = "Error: Form not changed"
        return validateupdate(request)

    return JsonResponse({})
    
    
def validateupdate(request):
    data = dict(request.POST.lists()).get("data[]")
    if(dict(request.POST.lists()).get("view")[0] != "rules"): 
        returndict = {0: ["accNameUpdate",[]],
                      2: ["IndateUpdate",[]],
                      3: ["OutdateUpdate",[]],
                      4: ["amtlineUpdate",[]],
                      5: ["amtunitUpdate", []],
                      6: ["costpercentUpdate",[]],
                      7: ["pricepercentUpdate",[]],
                      9:["annualUpdate",[]],
                      8:["monthlyUpdate",[]]}
        if(request.session.get('error',False)):
                returndict[0][1].append(request.session['message'])
                request.session['error'] = False
                return JsonResponse(returndict)
        if(data[0] != ""):
            quer = AccrualD.objects.using('Accrual').filter(AccrualName=data[0])
            if not quer.exists():
                returndict[0][1].append("Error: accrual name does not exist")
        if( data[2] != "" and data[3] != "" and int(data[2].replace("-","")) > int(data[3].replace("-",""))):
            returndict[2][1].append("Error: InEffectiveDate larger than OutEffectiveDate")
        if(data[5] != "" and not data[5].replace('.','').isnumeric()):
            returndict[5][1].append("Error: amt per line is not numeric")
        if(data[6] != "" and not data[6].replace('.','').isnumeric()):
            returndict[6][1].append("Error: amt per unit is not numeric")
        if(data[7] != "" and not data[7].replace('.','').isnumeric()):
            returndict[7][1].append("Error: percent of cost is not numeric")
        if(data[8] != "" and not data[8].replace('.','').isnumeric()):
            returndict[8][1].append("Error: percent of price is not numeric")
        if(data[7] != "" and (float(data[7])/100 >= 10 or float(data[7])/100 <= -10)):
            returndict[7][1].append("Error: percent of cost is too big")
        if(data[8] != "" and (float(data[8])/100 >= 10  or float(data[8])/100 <= -10)):
            returndict[8][1].append("Error: percent of price is too big")
        if(checklength(data[5:9],"") < 3):
            returndict[5][1].append("Error: Only 1/4 fields can be specified")
            returndict[6][1].append("Error: Only 1/4 fields can be specified")
            returndict[7][1].append("Error: Only 1/4 fields can be specified")
            returndict[8][1].append("Error: Only 1/4 fields can be specified")
        if(data[9] != "" and not data[9].replace('.','').isnumeric()):
            returndict[9][1].append("Error: monthly max is not numeric")
        if(data[10] != "" and not data[10].replace('.','').isnumeric()):
            returndict[10][1].append("Error: annual max is not numeric")
        return JsonResponse(returndict)
    else:
        returndict = {
        1:["uprulenum",[]],
        2:["upruleseq",[]],
        8:["uptstval",[]],
        9:["upIndaterul",[]],
        10:["upoutdaterul",[]]
        }
        if(request.session.get('error',False)):
                returndict[1][1].append("Error: Form Submitted with empty values")
                request.session['error'] = False
                
        if(data[1] != "" and not data[1].replace('.','').isnumeric()):
            returndict[1][1].append("Error: rule number is not numeric")
        if(data[2] != "" and not data[2].replace('.','').isnumeric()):
            returndict[2][1].append("Error: rule sequence number is not numeric")
        if((data[7] == "LS" or data[7] == "NS") and verifyWhitespace(data[8])):
            returndict[8][1].append("Error: whitespace in List")
        if( data[9] != "" and data[10] != "" and int(data[9].replace("-","")) > int(data[10].replace("-",""))):
            returndict[9][1].append("Error: InEffectiveDate larger than OutEffectiveDate")
        return JsonResponse(returndict)


def update(request):
    print(dict(request.POST.lists()))
    data = json.loads(dict(request.POST.lists()).get("data")[0])
    view = dict(request.POST.lists()).get("view")[0]
    checked = dict(request.POST.lists()).get("checked")[0]
    objs = None
    print(checked)
    if(view != "rules"):
        objs = AccrualD()
        j = 0
        for i in AccrualD._meta.get_fields():
            if(i.name == "InEffectiveDate" or i.name =="OutEffectiveDate" or i.name == "InvoiceByDate"):
                strs = data[j]
                data[j] = strs.replace("-","")
            if(i.name == "CostPercent" or i.name == "PricePercent"):
                if(data[j] != ""):
                    nums = float(data[j])
                    data[j] = nums/100.0
            if(j >= len(data) or data[j] == ""):
                if(i.get_internal_type() == "DecimalField"):
                    setattr(objs,i.name,0)
                else:
                    setattr(objs,i.name,None)
            else:
                if(i.get_internal_type() == "DecimalField"):
                    setattr(objs,i.name, float(data[j]))
                else:
                    setattr(objs,i.name,data[j])
            j+=1
        if(checked == 'false'):
            objs.save(using='Accrual')
            return redirect('/accruals/?view=definition&queryrule=' + data[0])
        else:
            AccrualR.objects.filter(RuleName=data[0]).delete()
            objs.delete()
        return redirect('/accruals/?view=definition')

    else:
        primary_key = data[-1]
        j = 0
        objs = AccrualR()
        for i in AccrualR._meta.get_fields():
            if(i.name == "InEffectiveDate" or i.name =="OutEffectiveDate"):
                strs = data[j]
                data[j] = strs.replace("-","")
            if(j >= len(data) or data[j] == ""):
                if(i.name == AccrualR._meta.pk.name):
                    setattr(objs,i.name,primary_key)
                elif(i.get_internal_type() == "DecimalField"):
                    setattr(objs,i.name,0)
                else:
                    setattr(objs,i.name,None)
            else:
                if(i.get_internal_type() == "DecimalField"):
                    setattr(objs,i.name, float(data[j]))
                else:
                    setattr(objs,i.name,data[j])
            j+=1
        if(checked == 'false'):
            objs.save(using='Accrual')
        else:
            objs.delete()
        return redirect('/accruals/?view=definition&queryrule=' + data[0])


    
def populate(request):
    data = dict(request.POST.lists())
    indate =""
    outdate=""
    if(data.get("definition",False)):
        for i in AccrualD.objects.filter(AccrualName = data.get("definition")[0].rstrip()):
            i.InEffectiveDate = str(i.InEffectiveDate)
            i.OutEffectiveDate = str(i.OutEffectiveDate)
            indate = i.InEffectiveDate[0:4] + "-" + i.InEffectiveDate[4:6] + "-" + i.InEffectiveDate[6:8]
            outdate = i.OutEffectiveDate[0:4] + "-" + i.OutEffectiveDate[4:6] + "-" + i.OutEffectiveDate[6:8]

            
    context = {
    
    "indate" : indate,
    "outdate" : outdate
    
    }
    return JsonResponse(context)
def deletevalidate(request):
    data = dict(request.POST.lists()).get("data[]")
    view = dict(request.POST.lists()).get("view")[0]
    exclude = [5,6,7,8] if view == "definition" else []
    for i in range(len(data)):
        if(data[i] == "" and not i in exclude):
            request.session['error'] = True
            request.session['message'] = "Error: Form Submitted with empty values"
            return validateupdate(request)
    return JsonResponse({})

def filevalidate(lists,view):
    data = lists
    error = False
    if(view != "rules"): 
        quer = AccrualD.objects.using('Accrual').filter(AccrualName=data[0])
        if quer.exists():
            error = True
        if(int(data[2].replace("-","")) > int(data[3].replace("-",""))):
            error = True
        if(data[4] != "" and not data[4].replace('.','').isnumeric()):
            error = True
        if(data[5] != "" and not data[5].replace('.','').isnumeric()):
            error = True
        if(data[6] != "" and not data[6].replace('.','').isnumeric()):
            error = True
        if(data[7] != "" and not data[7].replace('.','').isnumeric()):
            error = True
        if(checklength(data[4:8],"") < 3):
            error = True
        if(not data[8].replace('.','').isnumeric()):
            error = True
        if(not data[9].replace('.','').isnumeric()):
            error = True
    else:
        if(not data[1].replace('.','').isnumeric()):
            error = True
        if(not data[2].replace('.','').isnumeric()):
            error = True
    return error

def files(request):
    newfile = request.FILES['csv'].read().decode('utf-8')
    view = request.POST['view']
    readers = csv.reader(StringIO(newfile), delimiter=',')
    next(readers)
    writer = csv.writer
    linenumber = 1
    sendfile = False
    open("problems.txt", "w+").close()
    for data in readers:
        try:
            objs = AccrualD() if view == "definition" else AccrualR()
            attributes = AccrualD._meta.get_fields() if view=="definition" else AccrualR._meta.get_fields()
            validated = filevalidate(list(data), view)
            if(view == "definition" and validated):
                j = 0
                for i in AccrualD._meta.get_fields():
                    if(i.name == "InEffectiveDate" or i.name =="OutEffectiveDate"):
                        strs = data[j]
                        data[j] = strs.replace("-","")
                    if(j >= len(data) or data[j] == ""):
                        if(i.get_internal_type() == "DecimalField"):
                            setattr(objs,i.name,0)
                        else:
                            setattr(objs,i.name,None)
                    else:
                        if(i.get_internal_type() == "DecimalField"):
                            setattr(objs,i.name, float(data[j]))
                        else:
                            setattr(objs,i.name,data[j])
                    j+=1
            elif(validated):
                j = 0
                for i in AccrualR._meta.get_fields():
                    if(i.name == "InEffectiveDate" or i.name =="OutEffectiveDate"):
                        strs = data[j]
                        data[j] = strs.replace("-","")
                    if(i.name == "SQL_ID"):
                        print("hi")
                    elif(j >= len(data) or data[j] == ""):
                        if(i.get_internal_type() == "DecimalField" or i.get_internal_type =="IntegerField"):
                            setattr(objs,i.name,0)
                        else:
                            setattr(objs,i.name,None)
                    else:
                        if(i.get_internal_type() == "DecimalField"):
                            setattr(objs,i.name, float(data[j]))
                        elif(i.get_internal_type() == "IntegerField"):
                            setattr(objs,i.name,int(data[j]))
                        else:
                            setattr(objs,i.name,data[j])
                    j+=1
            else:
              with open("problems.txt","a+") as f:
                f.writerow("Error On Line" + str(linenumber)) 
                sendfile = True
            objs.save(using='Accrual')

        except:
            with open("problems.txt","a+") as f:
                f.write("Error On Line" + str(linenumber))
                sendfile = True
        linenumber +=1      
    if(sendfile):
        return FileResponse(open("problems.txt","rb"))
    return JsonResponse({})


def filedownload(request):
    files = open("answers.csv","w+")
    writers = csv.writer(files)
    views = request.POST['view']
    request = None
    columns = []
    if(views != "rules"):
        columns = [ i.name for i in AccrualD._meta.get_fields()]
        request = AccrualD.objects.using('Accrual').all()
    else:
        columns = [ i.name for i in AccrualR._meta.get_fields()]
        views = "rules"
        request = AccrualR.objects.using('Accrual').all()
    response = []
    writers.writerow(columns)
    for row in request:
        data = []
        for i in range(0,len(columns)):
            field_object = AccrualD._meta.get_field(columns[i]) if views == "definition" else AccrualR._meta.get_field(columns[i])
            data.append(field_object.value_from_object(row))
        writers.writerow(data)
    return FileResponse(open("answers.csv","rb"))
    
    
    
def inputs(request):
    models = Dropdown.objects.all()
    response = []
    columns = [ i.name for i in Dropdown._meta.get_fields()]

    for row in models:
        data = {}
        for i in range(0,len(columns)):
            field_object = Dropdown._meta.get_field(columns[i])
            data[columns[i]] = field_object.value_from_object(row).rstrip() if isinstance(field_object.value_from_object(row), str) else field_object.value_from_object(row)
        response.append(data)
    context = {"alldata" : response,
               "cols" : columns}
    return render(request,"accruals\\inputs.html",context)
    
def writeinputs(request):
    print(request.POST)
    ids = request.POST.getlist('id')[0]
    data = request.POST.getlist('arr[]')
    print(data)
    if(data == ['','',''] and ids != ''):
        objs = Dropdown(ids = ids, view_name = data[0], entry_name = data[1], value_name=data[2])
        objs.delete()
        return HttpResponse()
    elif(data == ['','',''] and ids == ''):
        return HttpResponse()
    if(ids == ''):
        objs = Dropdown(view_name = data[0], entry_name = data[1], value_name=data[2])
    else:
        objs = Dropdown(ids = ids, view_name = data[0], entry_name = data[1], value_name=data[2])
    objs.save()
    return HttpResponse()