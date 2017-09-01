'use strict';

angular.module('de.apps.bre', [])
    .controller('breController', function($scope, $http) {
        $scope.send = function(text) {
            if($scope.breForm.$valid) {
                $http.post('/bre/api', {text:text}).then(function(response) {
                    $scope.response = response;
                })
            }
        }
    });