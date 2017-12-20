'use strict';

angular.module('de.apps.bre', ['de.apps'])

.controller('breController', function($scope, $http) {
    $scope.send = function(text) {
        if($scope.breForm.$valid) {
            $http.post('/bre/api', {text:text}).then(function(response) {
                delete $scope.sents;
                delete $scope.error;
                if(response.data.results.error) {
                    $scope.error = response.data.results.error
                } else {
                    $scope.sents = response.data.results;
                }
            }, function(data) {
                delete $scope.sents;
                $scope.error = data.statusText;
            })
        }
    }
});