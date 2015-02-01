# -*- coding: utf-8 -*-
import os
import datetime, json, urllib, urllib2
import shutil

from django.shortcuts import render_to_response
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.template.context import RequestContext

from django.views.decorators.http import require_http_methods, require_GET, require_POST

import pysolr

SOLR_HOST = '192.168.10.17'
SOLR_HOST = 'localhost'
SOLR_URL = 'http://' + SOLR_HOST + ':8983/solr/filmes/select?'
MEDIA_FOLDER = "D:/srv/Apache24/www/apache.marco.br/media/filmes/"

def index(request):
    return render_to_response('filmes/index.html',
           {},
           context_instance=RequestContext(request))

def get_filmes(request):
    url = SOLR_URL
    qs = request.META['QUERY_STRING']
    url += qs
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

    url = SOLR_URL + "q=*:*&rows=0&wt=json&json.nl=arrarr&indent=true&facet=true&facet.field=imdbID_s&facet.mincount=2"
    r = urllib.urlopen(url).read()
    dados = json.loads(r)
    retorno = []
    
    facets_solr = dados["facet_counts"]["facet_fields"]["imdbID_s"]

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
 
def _exclui_info_file(path=""):
    discos = get_discos_win32()
    discos_sn = {}
    for disco in discos:
        sn = discos[disco]['serial_number']
        discos_sn[sn] = disco
        


    for id in ids:
        r = solr.search(q='id:"' + id + '"')
        
        doc = r.docs[0]
        path = discos_sn[doc['disk_sn_s']] + '/filmes/' + doc['disk_path_s']
        print id, r.hits, path
        if os.path.exists(path):
            shutil.rmtree(path)
            if os.path.exists(path):
                print "erro nao excluiu",path
                return
        exclui_solr(id=id)
        
def _get_discos_win32():
    discos = {}
    #import win32api
    #ll = win32api.GetLogicalDriveStrings().split('\\'+chr(0x0))[:-1]
    ll = ["g:","h:"]
    for l in ll:
        pth = l + "/filmes/disco.json"
        if  os.path.exists(pth):
            discos[l] =  json.load(open(pth))
    return discos
    

def _get_info_imdb(id):
    id = "%07d" % int(id)
    url = 'http://www.omdbapi.com/?i=tt' + id + '&plot=full&r=json&tomatoes=true'
    d = urllib.urlopen(url).read()
    info = json.loads(d)
    return info

def _grava_info_imdb(path,dados):
    F = open( path + '/imdb.json','w')

    json.dump(dados,F,indent=4)
    F.close()
    return 1

def _get_imdbid_jpg(path):
    # Pesquisa em uma pasta se há um jpg com nome numérico. 
    # Se houver retorna este número 
    files = os.listdir(path)
    imdb_id = 0
    for f in files:
        if '.jpg' in f.lower():
            (nm,ext) = f.lower().split('.')
            if ext == 'jpg' and nm.isdigit():
                imdb_id = nm
                break  
    return "%07d" % int(imdb_id)
    #return imdb_id
    
def refaz_registro_filme(request):

    id = request.GET.get('id','')
    imdb_id = request.GET.get('imdb_id','')
    img = request.GET.get('img','')
    now = datetime.datetime.now()
    
    campos_int = ["tomatoMeter","tomatoFresh","imdbVotes","tomatoRotten","tomatoUserReviews"
                  "tomatoUserMeter","tomatoReviews","Metascore"]
    campos_flt = ["imdbRating","tomatoRating","tomatoUserRating"]
    campos_dt = ["Released","last_update"]

    campos_mv = ["Language","Genre","Country", "Writer","Director","Actors"]

    campos_ndx = ["Title","Country","Plot", "Writer","Director","Actors"]

    campos_t = ['Plot',"tomatoConsensus"]

    discos = _get_discos_win32()
    discos_sn = {}
    for disco in discos:
        sn = discos[disco]['serial_number']
        discos_sn[sn] = disco
        

    solr = pysolr.Solr('http://' + SOLR_HOST + ':8983/solr/filmes/', timeout=10)

    if not id:
        retorno = {'status': False,'msg':"Nao foi informado um ID"}
    else:
        r = solr.search(q='id:"' + id + '"')
        
        doc = r.docs[0]
        path = discos_sn[doc['disk_sn_s']] + '/filmes/' + doc['disk_path_s']
        
        if not imdb_id:
            if img:
                imdb_id = doc['imdbID_s'].split('tt')[1]
                shutil.copyfile(path + '/' + img ,path + '/' + imdb_id + '.jpg')
            else:
                # verifica se ha um jpg com o id do imdb no nome
                imdb_id = _get_imdbid_jpg(path)        
            
        if not imdb_id:
            retorno = {'status': False,'msg':"Nao foi encontrado um jpg com o id do IMDB"}
        else:
        
            # Pega as informações na internet
            info = _get_info_imdb(imdb_id)
            if info["Response"] == "False":
                retorno = {'status': False,'msg': imdb_id + ' - ' + info['Error']}
            else:
            
                # Remove o info_file antigo
                if os.path.exists(path + '/imdb.json'):
                    os.rename(path + '/imdb.json',path + '/imdb_' + now.strftime("%Y%m%d_%H%M%S") + '.json')
                    
                # Verifica se a imagem jah estah na pasta media. Se nao estiver copia
                try:
                    if not os.path.exists(MEDIA_FOLDER + imdb_id + '.jpg'):
                        shutil.copyfile(path + '/' + imdb_id + '.jpg' ,MEDIA_FOLDER + imdb_id + '.jpg')
                except:
                    pass
                dados = {
                    'nome': path.split('/')[-1],
                    'last_update': now.strftime("%Y-%m-%d %H:%M:%S")
                }
                dados.update(info)  
                kk = dados.keys()
                for k in kk:
                    if dados[k] == 'N/A': dados.pop(k)
                dados.pop("Response")

                
                _grava_info_imdb(path,dados)

                dados['disk_name']=doc['disk_name_s']
                dados['disk_sn']=doc['disk_sn_s']
                dados['disk_path']=doc['disk_path_s']

                dados_solr = {}                
                
                for k in dados:
                    v = dados[k]
                    if v == 'N/A':continue
                    
                    #print k,v 
                    #print
                    
                    if k in campos_int:
                        ks = k + "_i"
                        v = v.replace(',','')
                    elif k in campos_flt:
                        ks = k + "_f"
                        
                    elif k in campos_mv:
                        ks = k + "_ss"
                        v = [x.strip() for x in v.split(',')]
                    elif k in campos_t:
                        ks = k + "_t"   
                    elif k in campos_dt:
                        ks = k + "_dt"  
                        if k == "Released":
                            v = datetime.datetime.strptime(v,"%d %b %Y")
                            
                        elif k =="last_update":
                            v = datetime.datetime.strptime(v,"%Y-%m-%d %H:%M:%S")
                        else:
                            print("Erro - campo data não tratado")
                            return
                    else:
                        ks = k + "_s"
                    dados_solr[ks] = v
                    
                
                dados_solr['id']=doc['id']
                solr.delete(q="id:" + id)
                solr.commit()
                solr.add([dados_solr],commitWithin="10000")
                solr.commit()
                retorno = {'status': True,
                    'msg':"Alterado o id %s com sucesso em %s" % (id,now.strftime("%Y-%m-%d %H:%M:%S"))
                }
    
    
    return HttpResponse( json.dumps(retorno,indent=True), "application/json")    

def filmes_imagens(request):
    discos = _get_discos_win32()
    discos_sn = {}
    for disco in discos:
        sn = discos[disco]['serial_number']
        discos_sn[sn] = disco
        
    solr = pysolr.Solr('http://' + SOLR_HOST + ':8983/solr/filmes/', timeout=10)
    r = solr.search(q="*:*",rows=10000,**{'fl':"id,imdbID_s,Title_s,nome_s,disk_path_s,disk_sn_s,Director_ss"})
    dados={}
    retorno = "<h1>Filme - Imagem</h1>"
    dados['hits'] = r.hits
    docs_sem_imagem = [] 
    total = 0
    for doc in r.docs:
        img = MEDIA_FOLDER + doc['imdbID_s'].split('tt')[1] + '.jpg'
        if not os.path.exists(img):
            total +=1
            pth = discos_sn[doc['disk_sn_s']] + '/filmes/' + doc['disk_path_s']
            #doc['pth']=pth
            ff = os.listdir(pth)
            doc['folder_imgs'] = []
            for f in ff:
                ext = f.split('.')[-1].lower()
                if ext == 'jpg':
                    doc['folder_imgs'].append(f)
            docs_sem_imagem.append(doc)
    dados['total']=total
    dados['docs'] = docs_sem_imagem
    
    return HttpResponse( json.dumps(dados,indent=True), "application/json")
    return render_to_response('filmes/filmes_imagens.html',
           {'dados':dados})
  
    
    
    
    
    