from django.db import models
from django.contrib.auth.models import User
from datetime import date

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0

# Create your models here.

    
class Organization(models.Model):
    name = models.CharField(max_length = 100)
    

class RecurringShift(models.Model):
    # From stackoverflow
    # http://stackoverflow.com/questions/5966629/django-days-of-week-representation-in-model
    name = models.CharField(max_length = 100)
    dayMo = models.BooleanField()
    dayTu = models.BooleanField()
    dayWe = models.BooleanField()
    dayTh = models.BooleanField()
    dayFr = models.BooleanField()
    daySa = models.BooleanField()
    daySu = models.BooleanField()
	
    startTime = models.IntegerField()
    endTime = models.IntegerField()
    startDate = models.DateField()
    endDate = models.DateField()
    user = models.ForeignKey(User)
    bonner = models.BooleanField()
    wlu_ce = models.BooleanField()
    organization = models.ForeignKey(Organization)
    last_logged = models.DateField()
        
    def happens_today(self):
        dayOfWeek = date.weekday(date.today())
        dayArray = [self.dayMo, self.dayTu, self.dayWe, self.dayTh, self.dayFr, self.daySa, self.daySu]
        return dayArray[dayOfWeek].numerator == 1 and date.today() >= self.startDate and date.today() <= self.endDate

    def last_logged_today(self):
        return self.last_logged == date.today()
    
    def log_hours(self):
        self.last_logged = date.today()
        self.save()
        for destination in self.destination_set.iterator():
            driver = webdriver.Firefox()
            driver.get(destination.url)
            for granule in destination.granule_set.iterator():
                if granule.action == "0":
                    select = Select(driver.find_element_by_name(str(granule.datum1)))
                    select.select_by_visible_text(str(granule.datum2))
                elif granule.action == "1":
                    driver.find_element_by_xpath(str(granule.datum1)).click()
                elif granule.action == "2":
                    textbox = driver.find_element_by_name(str(granule.datum1))
                    textbox.send_keys(str(granule.datum2))
                elif granule.action == "3":
                    element = driver.find_element_by_name(str(granule.datum1))
                    element.click()
                   
                

class Destination(models.Model):
    url = models.CharField(max_length=512)
    shift = models.ForeignKey(RecurringShift)
    
        
    
   
class Granule(models.Model):
    ACTIONS = (
        (0, 'select_by_name_click_by_visible_text'),
        (1, 'click_by_xpath'),
        (2, 'select_by_name_enter_text'),
        (3, 'click_by_name'),
    )
    action = models.CharField(max_length=1, choices=ACTIONS)
    datum1 = models.CharField(max_length=256)
    datum2 = models.CharField(max_length=256)
    datum3 = models.CharField(max_length=256)
    datum4 = models.CharField(max_length=256)
    datum5 = models.CharField(max_length=256)
    destination = models.ForeignKey(Destination)

        




