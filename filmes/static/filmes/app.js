'use strict';
console.log('app.js - iniciado');
angular.module('flmApp',['ngRoute','smart-table','ui.bootstrap','ngSanitize', 'ui.select']);

angular.module('flmApp').factory('flmService',function($http) {
    console.log('app.js - factory');
    

    return {
        get_facets: function(filtros) {
            return $http.get("/app/filmes/get_facets");
        },
        get_lista_duplicados: function() {
            console.log('app.js - get_lista_duplicados');
            return $http.get("/app/filmes/filmes_duplicados");
        },
        delete_solr: function(id) {
            console.log('app.js - delete_solr id=' + id);
            return $http.get("/app/filmes/delete_solr?id=" + id);
        },        
        get_filmes: function(filtros, p) {
            var fq=["Type_s:movie"];
            if (filtros != undefined) {
                for (var key in filtros) {
                    console.log('key=' + key + ' filtros[key].length='+ filtros[key].length);
                    if (key == 'Genre_ss' || key == 'Country_ss' || key == 'Language_ss') {
                        for (var i=0; i < filtros[key].length; i++) {
                            fq.push( key + ":" + filtros[key][i]);
                            console.log('i='+i +' fq=' + fq);
                        }
                    }
                    else {
                        fq.push(key + ":" + filtros[key]);
                    }
                }
            }
                  
            
            var  params = {
                    q:'*:*',
                    rows:10,
                    //fq:["Type_s:movie","Year_s:20*"],
                    fq:fq,
                    wt:'json', 
                    indent:'true',
                    sort: 'imdbRating_f desc',

            }            
            params = _.extend(params, p);     
            

            
            return $http.get("/app/filmes/get_filmes",{
                params: params
            });
        }
    }
});

angular.module('flmApp').config(['$routeProvider', '$httpProvider', function($routeProvider, $httpProvider, flmService) {
    console.log('app.js - config');
    
    $httpProvider.defaults.useXDomain = true;
    $httpProvider.defaults.withCredentials = true;
    delete $httpProvider.defaults.headers.common["X-Requested-With"];
    $httpProvider.defaults.headers.common["Accept"] = "application/json";
    $httpProvider.defaults.headers.common["Content-Type"] = "application/json";
    
    $routeProvider
        .when('/', {
            templateUrl: '/static/filmes/partials/main.html',
            controller: 'flmCtrl',
            resolve: {
                filmes: function(flmService) {

                    return flmService.get_filmes();
                },
                facets: function(flmService) {
                    return flmService.get_facets();
                }
            }
        })
        .when('/duplicados', {
            templateUrl: '/static/filmes/partials/dup.html',
            controller: 'dupCtrl',
            resolve: {
                filmes_duplicados: function(flmService) {

                    return flmService.get_lista_duplicados();
                }
            }
        }        
        )
        .otherwise({redirectTo: '/duplicados'});    
}]);


angular.module('flmApp').controller('dupCtrl', function($scope, flmService,filmes_duplicados) {
    
    $scope.filmes_duplicados = filmes_duplicados.data;
    //console.log("$scope.filmes_duplicados=" + $scope.filmes_duplicados);
    
    $scope.get_filmes_duplicados = function() {
        flmService.get_lista_duplicados()
        .success(function(data) {
            $scope.filmes_duplicados = data;
        })
        .error(function(erro) {
            alert("Erro na Pesquisa");
            console.log(erro);
        });          
    }
    
    $scope.delete_solr = function(id) {
        $scope.filmes_duplicados = [];        
        flmService.delete_solr(id)
        .success(function(data) {
            console.log(data);
            $scope.get_filmes_duplicados();           
          
        })
        .error(function(erro) {
            alert("Erro na Exclusão de " +id);
            console.log(erro);
        });
    }    
});

angular.module('flmApp').controller('flmCtrl', function($scope, flmService,filmes,facets) {
    $scope.filmes = filmes.data.response.docs;
    
    $scope.availableGenres = facets.data.Genre_ss;
    $scope.availableLanguages = facets.data.Language_ss;
    $scope.availableCountries = facets.data.Country_ss;

    $scope.filtros = {
        Genre_ss : [],
        Country_ss : [],
        Language_ss : []
    }
    $scope.params = {
        rows: 10,
        sort: 'imdbRating_f desc'
    }

    $scope.filtrosIsCollapsed = true;

    $scope.pesquisar = function() {
        $scope.filmes = [];
        flmService.get_filmes($scope.filtros, $scope.params)
        .success(function(data) {
            $scope.filmes = data.response.docs;
        })
        .error(function(erro) {
            alert("Erro na Pesquisa");
            console.log(erro);
        });
    }



});

