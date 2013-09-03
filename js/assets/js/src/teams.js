var App = angular.module('intranet', ['ngDragDrop', 'ui.bootstrap', 'ui.date'], function($locationProvider){
  $locationProvider.html5Mode(true);
});

$.fn.hasScrollBar = function() {
  return this.get(0).scrollHeight > this.height();
};
var resetScrolls = function(){
  var teams = $('.team-box ul'),
    users = $('.box-users ul');
  var scrollTeams = teams.hasScrollBar(),
    scrollUsers = users.hasScrollBar();
  if (scrollTeams) {
    teams.addClass('scroll');
  }
  if (scrollUsers) {
    users.parent().addClass('scroll-user');
  }
};

App.controller('oneCtrl', function($scope, $http, $dialog) {
  $scope.teams = [];
  $scope.users = [];

  $http.get('/api/users').success(function(data){
      $scope.users = data;

      $http.get('/api/teams').success(function(data){
        $scope.teams = data;
        _.each($scope.teams, function(team){
          team.users = _.filter($scope.users, function(user){
            return team.users.indexOf(user.id) !== -1;
          });
        });
      });
    resetScrolls()
  });


  $scope.onBeforeDrop = function(drop, drag){
    if(drop.indexOf(drag) !== -1) {
      return false;
    } else {
      var team = _.find($scope.teams, function(team){ return team.users == drop});
      team.dirty = true;
      return true;
    }
  };

  $scope.openModal = function(team){
      var d = $dialog.dialog({
          resolve: {
            $callerScope: function() {return $scope},
            team: function() {return team}
          }
        });
      d.open('team.html', 'teamCtrl');

  };

  $scope.save = function(team){
    var ids = _.pluck(team.users, 'id');
    $http.put('/api/teams/' + team.id, {
      users: ids
    }).success(function(data){
        team.dirty = false;
    });
  };

  $scope.deleteUser = function (item, team){
    var index = team.users.indexOf(item);
    team.users.splice(index, 1);
    team.dirty = true;
  };

  $scope.deleteTeam = function (team){
    var r = confirm("Press a button");
    if(r == true){
      $http.delete('/api/teams/' + team.id);
      var index = $scope.teams.indexOf(team);
      $scope.teams.splice(index, 1)
    }
  };

});

App.controller('teamCtrl', function($scope, $http, $timeout, dialog, $callerScope, team) {
  $scope.team = angular.copy(team || {users:[], name: '', img: '/api/images/teams/0'});
  $scope.swap_with_preivew = false;

  $scope.add = function(){
    $scope.form_submitted = true;
    if($scope.teamForm.$invalid) return;

    $http.post('/api/teams', {
      name: $scope.team.name,
      swap_with_preview: $scope.swap_with_preivew
    }).success(function(data){
        $scope.team.id = data.id;
        $scope.team.img = data.img;
        $callerScope.teams.push($scope.team);
        dialog.close();
    });
  };

  $scope.edit = function(){
    $scope.form_submitted = true;
    if($scope.teamForm.$invalid) return;

    $http.put('/api/teams/' + team.id, {
      name: $scope.team.name,
      swap_with_preview: $scope.swap_with_preivew
    }).success(function(data){
        team.name = $scope.team.name;
        team.img = team.img + '?t=' + (new Date().getTime());
        dialog.close();
    });

  };

  $scope.close = function(){
    dialog.close();
  };

  $timeout(function(){
    var $btn = $('#upload-btn');

    var up = new Uploader($btn, {
      url: '/api/preview?type=team',
      onLoad: function(e) {
        $('#my-avatar img').attr('src',e.file.url+'?t='+(new Date().getTime()));
      },
      onComplete: function(e) {
        $scope.swap_with_preivew = true;
        $scope.$apply();
      },
      onProgress: function(e) {},
      onAdd: function(e) {},
      onError: function(e) {}
    });

  }, 100);

  return false;

});

App.filter('format_time', function () {
    return function (text, length, end) {
      var result = ((parseFloat(text) * 60) / 60);
      var hours = Math.floor(result);
      var floatingPointPart = (result - hours);
      var minutes =  Math.round(floatingPointPart.toFixed(2) * 60);
      if (minutes < 10) {
        minutes = "0" + minutes;
      } else if (minutes === 0) {
        minutes = "00";
      }
      return hours + ":" + minutes;
    };
});

App.directive('watchchanges', function() {
    return function (scope, element, attrs) {
      var parent = element.closest('.parent');
      var ticket_id = parent.find('.ticket_id');
      var ticket_desc = parent.find('.ticket_desc');

      element.on('change', function(){
        var type = scope.ticketTypes[element.val()];

        if(type.value !== "M0"){
            ticket_id.val(type.value);
            ticket_id.prop('readonly', true);
            ticket_desc.val(type.desc);
        } else {
            ticket_id.val('');
            ticket_id.prop('readonly', false);
            ticket_desc.val('');
        }

        // Angular should know about changes
        scope.$apply(function () {
          if( attrs.id ) {
            var entry = _.find(scope.entries, function(entry){ return entry.id == attrs.id;});
            entry.ticket_id = ticket_id.val();
            entry.desc = ticket_desc.val();
          }else {
            scope.data.ticket_id = ticket_id.val();
            scope.data.time_desc = ticket_desc.val();
          }
        });
      });
    };
  });

App.factory('entriesData', function($rootScope){
  data = [];
  attrs = {};

  return {
      attrs: {},
      getData: function() {
        return data;
      },
      getAttrs: function() {
        return attrs;
      },
      mergeData: function(newData, boardcast){
        data.push(newData);
        if(boardcast){
          $rootScope.$broadcast("handleNewData");
        }
        return data;
      },
      mergeAttrs: function(newAttrs){
        return angular.extend(attrs, newAttrs);
      },
      reset: function(sure){
        data = [];
        attrs = {};
      }
  };
});

App.controller("TimeListCtrl", function($scope, $dialog, $http, $location, entriesData){
  ( function() {
    
    function pad(number) {
      var r = String(number);
      if ( r.length === 1 ) {
        r = '0' + r;
      }
      return r;
    }
 
    Date.prototype._toISOString = function() {
      return this.getUTCFullYear()
        + '-' + pad( this.getUTCMonth() + 1 )
        + '-' + pad( this.getDate() )
        + 'T' + pad( this.getUTCHours() )
        + ':' + pad( this.getUTCMinutes() )
        + ':' + pad( this.getUTCSeconds() )
        + '.' + String( (this.getUTCMilliseconds()/1000).toFixed(3) ).slice( 2, 5 )
        + 'Z';
    };
  
  }() );

  $scope.entries = entriesData.getData();
  $scope.total_time = 0;
  $scope.entriesDate = new Date();
  $scope.needs_justification = false;
  $scope.can_modify = true;
  $scope.dateOptions = {
      changeMonth: true,
      yearRange: '2000:-0',
      dateFormat: 'dd.mm.yy',
      showOn: "button",
      buttonImageOnly: true,
      buttonImage: "/static/img/calendar.gif",
  };
  $scope.ticketTypes = [
    {"value": "M0", "desc": "Ticket ID"},
    {"value": "M1", "desc": "Daily Standup"},
    {"value": "M2", "desc": "Planning meeting"},
    {"value": "M3", "desc": "Review meeting"},
    {"value": "M4", "desc": "Retrospective meeting"}
  ];

  $scope.$on("handleNewData", function(){
    $scope.entries = entriesData.getData();
    $scope.handlerEntriesData();
    console.log('update');
  });

  if($location.search().date){
    $scope.entriesDate = Date.parseExact($location.search().date, "d.M.yyyy");
  }
  $scope.modelDate = $scope.entriesDate.toString("dd.MM.yyyy");

  $scope.getEntries = function() {
    entriesData.reset();
    $http.get('/api/times?date=' + $scope.entriesDate._toISOString()).success(function(data){
      $scope.can_modify = data.can_modify;
      $scope.entries = data.entries;
      $scope.handlerEntriesData();

      // Add Data to factory
      _.each($scope.entries, function(entry){
        entriesData.mergeData(entry, false);
      });
      entriesData.mergeAttrs({can_modify: data.can_modify});
    });
  };
  $scope.getEntries($scope.entriesDate);
 
  $scope.handlerEntriesData = function(){
    $scope.total_time = 0;
    $scope.needs_justification = false;
    _.each($scope.entries, function(entry){
        if(_.any($scope.ticketTypes, function(v){ return v.value === entry.ticket_id; })){
            entry.ticket_type = entry.ticket_id;
        }else{
            entry.ticket_type = "M0";
        }

        if(Date.parseExact(entry.modified, "d.M.yyyy") > Date.parseExact(entry.date, "d.M.yyyy")){
          $scope.needs_justification = true;
        }
        $scope.total_time += entry.time;
    });
  };
 
  $scope.changeDateHandler =function(modelDate){
    $scope.entriesDate = Date.parseExact(modelDate, "d.M.yyyy");
    $location.search('date', $scope.entriesDate.toString('dd.MM.yyyy'));
    // Update Table
    $scope.getEntries();
  };

  $scope.nextDate = function() {
    $scope.entriesDate = $scope.entriesDate.add({days: 1});
    $location.search('date', $scope.entriesDate.toString('dd.MM.yyyy'));
    
    $scope.getEntries();
  };

  $scope.previousDate = function() {
    $scope.entriesDate.add({days: -1});
    $location.search('date', $scope.entriesDate.toString('dd.MM.yyyy'));
    
    $scope.getEntries();
  };
  
  $scope.openEdit = function(id, idx){
    $scope.projects = [];

    var entry = _.find($scope.entries, function(entry){ return entry.id == id;});
    entry.dirty = true;
    $http.get('/api/projects').success(function(data){
      $scope.projects = data.projects;
    });
  };

  $scope.submitEdit = function(id){
   var entry = _.find($scope.entries, function(entry){ return entry.id == id;});

    $http.put('/api/times/' + entry.id, {
      project_id: entry.project.project_id,
      ticket_id: entry.ticket_id,
      time: entry.time,
      description: entry.desc
    }).success(function(data){
      // Edit data
      var project = _.find($scope.projects, function(project){ return project.id == entry.project.project_id; });
      entry.project.client_name = project.client_name;
      entry.project.project_name = project.name;
      entry.dirty = false;
    });
  };

  $scope.closeEdit = function(id){
    var entry = _.find($scope.entries, function(entry){ return entry.id == id;});
    entry.dirty = false;
  };

  $scope.delete = function(idx){
    var entryToDelete = $scope.entries[idx];
    $http.delete('/api/times/' + entryToDelete.id).success(function(){
      $scope.entries.splice(idx, 1);
      $scope.handlerEntriesData();
    });
  };
});

App.controller("AddTimeEntryCtrl", function($scope, $dialog, $http, $location, $timeout, entriesData){
  $scope.showSelect = true;
  $scope.projects = [];
  $scope.can_modify = entriesData.getAttrs();
  $scope.ticketTypes = [
    {"value": "M0", "desc": "Ticket ID"},
    {"value": "M1", "desc": "Daily Standup"},
    {"value": "M2", "desc": "Planning meeting"},
    {"value": "M3", "desc": "Review meeting"},
    {"value": "M4", "desc": "Retrospective meeting"}
  ];

  $http.get('/api/projects').success(function(data){
    $scope.projects = data.projects;
  });

  $scope.submit = function(data){
    // Resolve projec_id
    var project = _.find($scope.projects, function(project){ return project.value == data.project_id; });

    $http.post("/api/times", {
      project_id: project.id,
      ticket_id: data.ticket_id,
      time: data.time,
      description: data.time_desc,
      timer: false,
      add_to_harvest: false
    }).success(function(data){
      entriesData.mergeData(data, true);
      $scope.reset();
    });
  };

  $scope.hideSelect = function() {
    $scope.showSelect = false;
  };

  $scope.reset = function() {
    $scope.data = angular.copy({});
    $scope.ticket_type = angular.copy('');
  };

  $scope.reset();

});

App.controller('AddEntryToOneBugsCtrl', function($scope, $http, entriesData){
  $scope.tasks = [];
  $scope.isLoading = true;

  $http.get('/api/bugs').success(function(data){
    _.each(data.bugs, function(task){
      // reset time
      task.time = "";
      $scope.tasks.push(task);
    });
    $scope.tasks_backup = angular.copy($scope.tasks);
    $scope.isLoading = false;
  });

  $scope.submit = function(data) {
    a = angular.copy(data);
    $http.post("/api/times", {
      project_id: a.project.id,
      ticket_id: a.id,
      time: a.time,
      description: a.desc,
      timer: false,
      add_to_harvest: false
    }).success(function(data){
      entriesData.mergeData(data, true);
    });
    data.time = ''; // reset
  };

});

App.controller("WrongTimeModalCtrl", function($scope, $dialog){
  $scope.dateOptions = {
    changeMonth: true,
    yearRange: '2000:-0',
    dateFormat: 'dd.mm.yy',
  };

  $scope.openModal = function(){
    var d = $dialog.dialog({
        resolve: {
          $callerScope: function() {return $scope}
        }
      });
    d.open('wrong_time_justification.html', 'WrongTime');
  };
});

App.controller("WrongTime", function($scope, dialog){
  $scope.close = function(){
    dialog.close();
  };
});
