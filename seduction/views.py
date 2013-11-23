from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.template import RequestContext

from seduction.models import RecurringShift
from seduction.models import Destination
from seduction.models import Granule
from seduction.models import Organization
from datetime import datetime
from datetime import date
from django.contrib.auth.decorators import login_required

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0

from django.shortcuts import redirect

def hourToText(hour):
    if hour % 12 != 0:
        if hour // 12 == 0:
            meridian = "am"
        else:
            meridian = "pm"
        return "%i %s" % (hour % 12, meridian)
    elif hour == 0:
        return "Midnight"
    return "Noon"

def minuteToText(minute):
    return "%02i" % (minute)
    
def formatToMinutes(timeS='6:30AM'):
    #format is just 6:30AM
    timeS = timeS.upper()
    if ':'not in timeS:
        timeS = timeS[:-2]+':00'+timeS[-2:]
        print(timeS)
    colon = timeS.find(':')
    hours = int (timeS[:colon])
    mins = int (timeS[colon+1:colon+3])
    time = hours*60+mins
    if 'PM' in timeS:
        time+=720
    return time


# Create your views here.
@login_required
def viewShift(request, shift_id):
    try:
        shift = RecurringShift.objects.get(pk = shift_id)
    except RecurringShift.DoesNotExist:
        raise Http404
    
    if (request.user.id != shift.user.id):
        return HttpResponse("Access Denied")
    
    context = RequestContext(request, {
        "shift": shift,
    })
    #return HttpResponse(shift.dayMo)
    return render(request, 'seduction/view.html', context)

@login_required
def editShift(request, shift_id):
	return HttpResponse("You are editing shift %s." % shift_id)

@login_required
def createShift(request):
    template = loader.get_template('seduction/create.html')
    context = RequestContext(request, {"organizations" : Organization.objects
    })
    return HttpResponse(template.render(context))

@login_required
def instantiateShift(request):
    dateFormat = "%m/%d/%Y"
    days = request.POST.getlist('days')
    ret = ""
    daySu,dayMo,dayTu,dayWe,dayTh,dayFr,daySa = [x in days for x in \
        ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", \
            "Saturday")]
    shiftName = str(request.POST.get("shiftName"))
    startTime = formatToMinutes(request.POST.get("startTime"))
    endTime = formatToMinutes(request.POST.get("endTime"))
    startDate = request.POST.get("startDate")
    newStartDate = datetime.strptime(startDate, dateFormat)
    endDate = request.POST.get("endDate")
    bonner = request.POST.get("bonner") == "on"
    wlu_ce = request.POST.get("wlu_ce") == "on"
    organization_id = request.POST.get("organization")
    
    print(bonner)
    newEndDate = datetime.strptime(endDate, dateFormat)
    newShift = RecurringShift(organization = Organization.objects.get(pk = int(organization_id)),
                              startTime = startTime, endTime = endTime, name=shiftName, \
        startDate = newStartDate, endDate = newEndDate, daySu = daySu, \
            dayMo = dayMo, dayTu = dayTu, dayWe = dayWe, dayTh = dayTh, \
                dayFr = dayFr, daySa = daySa, user = request.user, bonner = bonner, wlu_ce = wlu_ce, last_logged = date(1970, 1, 1))
    newShift.save()
    
    if (bonner):
        fundraising = request.POST.get("bonner_fundraising")
        position = request.POST.get("bonner_position")
        bonnerDest = Destination(url = "http://localhost/twitchard/lumberjack/dummy.html", shift = newShift)
        #http://wlu.bwbrs.org/log.taf
        bonnerDest.save()
        start_hh_granule = Granule(destination = bonnerDest, action = "0", datum1 = "start_hh", datum2 = hourToText(startTime // 60))
        end_hh_granule = Granule(destination = bonnerDest, action = "0", datum1 = "end_hh", datum2 = hourToText(endTime // 60))
        start_mm_granule = Granule(destination = bonnerDest, action = "0", datum1 = "start_mm", datum2 = minuteToText(((startTime % 60) // 15) * 15))
        end_mm_granule = Granule(destination = bonnerDest, action = "0", datum1 = "end_mm", datum2 = minuteToText(((endTime % 60) // 15) * 15))
        xPath = "//option[text()=\""+position+"\"]"
        shift_granule = Granule(destination = bonnerDest, action = "1", datum1 = xPath)      
        start_hh_granule.save()
        end_hh_granule.save()
        start_mm_granule.save()
        end_mm_granule.save()
        shift_granule.save()
    
    if (wlu_ce):
        
        wluCeDest = Destination(url = "http://localhost/twitchard/lumberjack/dummy2.htm", shift = newShift)
        wluCeDest.save()
        
        checkList = request.POST.getlist("wlu_ce_campus_program") + \
            request.POST.getlist("wlu_ce_type")

        
        #return HttpResponse(str(checkList))
        position = request.POST.get("wlu_ce_organization")
        organizationXPath = "//option[text()=\""+position+"\"]"
        organizationGranule = Granule(destination = wluCeDest, action = "1", datum1 = organizationXPath)      
        organizationGranule.save()
        
        
        hoursGranule = Granule(destination = wluCeDest, action = "2",
                               datum1 = "ctl00$ApplicationContentPlaceHolder$HoursHoursTextBox",
                               datum2 = str((((endTime - startTime) // 15)*15)/60))
        hoursGranule.save()
        
        studentOrganization = request.POST.get("wlu_ce_student_organization")
        
        studentOrganizationGranule = Granule(destination = wluCeDest, action = "2",
                               datum1 = "ctl00$ApplicationContentPlaceHolder$OtherOrganizationTextBox",
                               datum2 = studentOrganization)
        studentOrganizationGranule.save()
        checkboxValues = ["Ameri Corps", "Bonner", 
                          "Campus Garden", "Campus Kitchens",
                          "Community Based Research",
                          "Administrative", "Athletic/Recreation",
                          "Awareness Campaign"]
        xpathFormatter = "//label[text()=\"%s\"]/../input"
        checkboxGranules = [Granule(destination = wluCeDest, action = "1",
                                    datum1 = xpathFormatter % (x)) for x in checkboxValues \
                                        if x in checkList]
        for granule in checkboxGranules:
            granule.save()
        
        #//label[text()=\"Nabors\"]/../input
        #(startTime % 60) // 15
        
    
    
    
    #return HttpResponse(ret)
    return viewShift(request, newShift.id)

@login_required
def logShift(request, shift_id):
    try:
        shift = RecurringShift.objects.get(pk = shift_id)
    except RecurringShift.DoesNotExist:
        raise Http404
    if (request.user.id != shift.user.id):
        return HttpResponse("Access Denied")
    shift.log_hours()
    return redirect('/')
    
  
