# -*- coding: utf-8 -*-
#from django.conf.urls.defaults import *
from django.conf.urls import patterns, include, url
#patterns

import views 

urlpatterns = patterns('',
    (r'^$', views.index, {}, 'index'),
    (r'^get_filmes$', views.get_filmes, {}, 'get_filmes'),
    (r'^get_facets$', views.get_facets, {}, 'get_facets'),
    (r'^filmes_duplicados$', views.filmes_duplicados, {}, 'filmes_duplicados'),    
    (r'^delete_solr$', views.delete_solr, {}, 'delete_solr'),  
    (r'^refaz_registro_filme$', views.refaz_registro_filme, {}, 'refaz_registro_filme'),  
    (r'^filmes_imagens$', views.filmes_imagens, {}, 'filmes_imagens'),  
    
    
    (r'^teste$', views.teste, {}, 'teste'),    

    #(r'^get_municipios$', views.get_municipios, {}, 'get_municipios'),
    #(r'^dados_mun$', views.dados_mun, {}, 'dados_mun'),
    
     
)
