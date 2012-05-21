# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('geo.region.views',
    (r'user-region/$', 'getUserLocation'), # главная страница
    (r'user-region/autocomplete$', 'regionAjax'), # автодополнение городов
    (r'user-region/validate', 'regionValidate'), # проверка на валидность
    (r'user-region/submit', 'regionSubmit'), # проверка на валидность
    (r'user-region/set$', 'setUserLocation'), # установка региона
    (r'region/$', 'user_region'),
    (r'region/ajax_search$', 'user_region_ajax_search'),
    (r'region/ajax_validate$', 'user_region_validate'),
    (r'region/ajax_get_region$', 'user_region_get'),
    (r'region/submit', 'user_region_result'),

)