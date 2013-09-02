var App = angular.module('intranet', ['ngDragDrop', 'ui.bootstrap', 'ui.date']);

$.fn.hasScrollBar = function() {
  return $scope.entriesDate.get(0).scrollHeight > $scope.entriesDate.height();
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
      if (minutes == 0) {
        minutes = "00";
      }
      return hours + ":" + minutes;
    };
});

App.controller("TimeListCtrl", function($scope, $dialog, $http, $location, $timeout){
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

  $scope.entries = [];
  $scope.total_time = 0;
  $scope.entriesDate = new Date();
  $scope.needs_justification = false;
  $scope.can_modify = true;
  $scope.dateOptions = {
      changeMonth: true,
      yearRange: '1900:-0',
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

  if($location.search().date){
    $scope.entriesDate = Date.parseExact($location.search().date, "d.M.yyyy");
  }
  $scope.modelDate = $scope.entriesDate.toString("dd.MM.yyyy");


  $scope.$watch('ticket_type',function(newValue, oldValue){
      
    console.log(newValue);
  });

  $scope.getEntries = function() {
    $http.get('/api/times?date=' + $scope.entriesDate._toISOString()).success(function(data){
      $scope.can_modify = data.can_modify;
      $scope.entries = data.entries;
      $scope.handlerEntriesData();
    });
  };
  $scope.getEntries($scope.entriesDate);
  
  $scope.handlerEntriesData = function(){
    $scope.total_time = 0;
    $scope.needs_justification = false;
    _.each($scope.entries, function(entry){
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
  
  $scope.openEdit = function(id){
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
