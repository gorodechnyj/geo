# -*- coding: utf-8 -*-
'''
Created on 26.10.2011

@author: gorodechnyj
'''

from django.contrib.gis.db import models
from .region import Region

class City(models.Model):
    name = models.CharField(max_length=50)
    rid = models.ForeignKey(Region)
    type = models.CharField(max_length=10)
    code = models.CharField(max_length=13)
    
    class Meta:
        app_label = "region"
    
    def __unicode__(self):
        return self.name