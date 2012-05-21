# -*- coding: utf-8 -*-
'''
Created on 26.10.2011

@author: gorodechnyj
'''

from django.contrib.gis.db import models

class Region(models.Model):
    name      = models.CharField(max_length=50)
    type      = models.CharField(max_length=10)
    full_name = models.CharField(max_length=200)
    code      = models.CharField(max_length=13)

    class Meta:
        app_label = "region"
    
    def __unicode__(self):
        return self.name + u' ' + self.type