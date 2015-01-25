# -*- coding: utf-8 -*-
import os
import datetime, json, urllib, urllib2

from django.shortcuts import render_to_response
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext

from django.views.decorators.http import require_http_methods, require_GET, require_POST

import pysolr

#SOLR_URL = 'http://localhost:8983/solr/filmes/select?'
SOLR_HOST = '192.168.10.17'
SOLR_URL = 'http://' + SOLR_HOST + ':8983/solr/filmes/select?'

def index(request):
    return render_to_response('filmes/index.html',
           {},
           context_instance=RequestContext(request))

def get_filmes(request):
    url = SOLR_URL
    qs = request.META['QUERY_STRING']
    url += qs
    #return HttpResponse(url,"text/plain")
    r = urllib.urlopen(url).read()

    return HttpResponse(r,"application/json")

def teste(request):
    p = "/mnt/seagate/Filmes/2012"
    x = os.path.exists(p)
    ll = os.listdir(p)
    retorno = "p="+ p + " x=" + str(x) + "\n\nll=" + str(ll)
    return HttpResponse(retorno,'text/plain')     

def delete_solr(request):
    si = pysolr.Solr('http://' + SOLR_HOST + ':8983/solr/filmes/', timeout=10)
    id = request.GET.get('id','')
    if id:
        url = SOLR_URL + "q=id:" + id + "&rows=1&wt=json&json.nl=arrarr&indent=true"
        r = si.search(q="id:"+ id,rows=1)
        if r.hits:
            si.delete(id=id)
            si.commit()
            r2 = si.search(q="id:"+ id,rows=1)
            if not r2.hits:
                retorno = {'status': True, 'msg':"Excluiu " + id}
            else:
                retorno = {'status': False, 'msg':"Nao Excluiu " + id}
        else:
            retorno = {'status': False, 'msg':"Nao encontrou " + id}            
    else:
        retorno = {'status': False,'msg':"Nao foi informado um ID"}
        
    return HttpResponse( json.dumps(retorno), "application/json")
    
    
def filmes_duplicados(request):
    #/dev/sdb1: LABEL="TOSHIBA EXT" UUID="C2E085DBE085D5D7" TYPE="ntfs" PARTUUID="61ac85ae-01" 
    #/dev/sdc1: LABEL="Seagate Expansion Drive" UUID="C806D33C06D329E8" TYPE="ntfs" 
    url = SOLR_URL + "q=*:*&rows=0&wt=json&json.nl=arrarr&indent=true&facet=true&facet.field=imdbID_s&facet.mincount=2"
    r = urllib.urlopen(url).read()
    dados = json.loads(r)
    retorno = []
    
    
    facets_solr = dados["facet_counts"]["facet_fields"]["imdbID_s"]
    #return HttpResponse(str(facets_solr),'text/plain')

    for (imdbID, qtde) in facets_solr:
        url = SOLR_URL + "q=imdbID_s:" + imdbID + "&rows=10&fl=Title_s,disk_path_s,disk_name_s,id&wt=json&indent=true"
        r = urllib.urlopen(url).read()
        docs = json.loads(r)['response']['docs']
        for doc in docs:
            (dsk,path) = doc['disk_path_s'].split(':')
            if dsk == 'g':
                dsk = u'/mnt/seagate'
                path = path.replace('/filmes/', '/Filmes/' )
            else:
                dsk = u'/mnt/toshiba'
            dsk_path = dsk + path
            pasta_existe = os.path.exists(dsk_path)
            if pasta_existe:
                filelist = os.listdir(dsk_path)
            else:
                filelist = []

            
            retorno.append({
                'imdbID':imdbID,
                'id':doc['id'],
                'qtde':qtde,
                'filelist': filelist, 
                #'filme_existe': os.path.exists(dsk_path.encode('latin1')),
                'pasta_existe': pasta_existe,
                'title': doc['Title_s'],
                'disk_name': doc['disk_name_s'],
                'disk_path': dsk_path
            })
        
    return HttpResponse(json.dumps(retorno),"application/json")
        

def get_facets(request):
    url = SOLR_URL + "q=*:*&rows=0&wt=json&indent=true&facet=true&facet.field=Genre_ss&facet.field=Country_ss"
    url += "&facet.field=Language_ss&facet.limit=200&facet.sort=index&facet.mincount=1"

    r = urllib.urlopen(url).read()
    dados = json.loads(r)
    facets = {}
    facets_solr = dados["facet_counts"]["facet_fields"]
    for facet in facets_solr:
        facets[facet]=[]
        for i in range(0,len(facets_solr[facet]),2):
            facets[facet].append(facets_solr[facet][i])

    facets_json = json.dumps(facets)

    return HttpResponse(facets_json ,"application/json")
    
