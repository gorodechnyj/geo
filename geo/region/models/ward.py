# -*- coding: utf-8 -*-
'''
Created on 24.05.2012

@author: gorodechnyj
'''

from django.contrib.gis.db import models
from .city import City

class Ward(models.Model):
    name      = models.CharField(max_length=100)
    city = models.ForeignKey(City)    

    class Meta:
        app_label = "region"
    
    def __unicode__(self):
        return self.name