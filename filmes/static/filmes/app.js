'use strict';

angular.module('flmApp',['ngRoute','ui.bootstrap','ngSanitize', 'ui.select']);

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
        .when('/filmes_imagens', {
            templateUrl: '/static/filmes/partials/filmes_imagens.html',
            controller: 'fimgCtrl',
            resolve: {
                filmes: function(flmService) {

                    return flmService.filmes_imagens();
                }
            }
        }        
        )        
        .otherwise({redirectTo: '/duplicados'});    
}]);




