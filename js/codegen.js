'use strict';

angular.module('de.apps.codegen', ['de.apps'])
.controller('codegenController', function($scope, $http) {
    $scope.send = function(text) {
        if($scope.codegenForm.$valid) {
            $scope.loading = true;
            $http.post('/apps/codegen/api', {query:text}).then(function(response) {
                delete $scope.code;
                delete $scope.error;
                $scope.loading = false;
                if(response.data.results.error) {
                    $scope.error = response.data.results.error;
                } else {
                    $scope.code = response.data.results.code;
                }
            }, function(data) {
                $scope.loading = false;
                delete $scope.code;
                $scope.error = data.statusText;
            })
        }
    }
}).run(function($rootScope, $timeout){
    $rootScope.$on('$stateChangeSuccess', function() {
        $timeout(function() {Prism.highlightAll()}, 0);
    });
});