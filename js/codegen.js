'use strict';

angular.module('de.apps.codegen', ['de.apps'])

.controller('codegenController', function($scope, $http) {
    $scope.send = function(text) {
        if($scope.codegenForm.$valid) {
            $http.post('/codegen/api', {text:text}).then(function(response) {
                delete $scope.code;
                delete $scope.error;
                if(response.data.results.error) {
                    $scope.error = response.data.results.error;
                } else {
                    $scope.code = response.data.results;
                }
            }, function(data) {
                delete $scope.code;
                $scope.error = data.statusText;
            })
        }
    }
});