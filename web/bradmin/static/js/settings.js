console.log('settings.js');

var App = Em.Application.create({
    ready: function () { console.log('ready'); App.init()},
});

App.init = function() {
    $.ajax({
	url: "settings/lowpan",  
	type: "GET",  
	dataType: "json",  
	contentType: "application/json",  
	success: function(data) {
	    App.lowpan.set('url', data.url);
	    App.lowpan.set('apikey', data.password);
	}
    });  
}

App.password = Ember.Object.create({
    ChangeWait: false,
    ChangeState: 'none',
    pass1: "",
    pass2: "",
    changepass: function() { 
	if(this.get('pass1') == this.get('pass2'))
	{
	    this.set('ChangeWait', true);
	    $.ajax({
		url: "settings/newpass",
		type: "POST",
		dataType: "json",
		contentType: "application/json",
		data: JSON.stringify({ "password": this.get('pass1') }),
		success: function(data) {
		    App.password.set('ChangeWait', false);
		    App.password.set('pass1','');
		    App.password.set('pass2','');
		}
	    });  
	}	
    },
    empty: function() {
	var p1 = this.get('pass1');
	var p2 = this.get('pass2');
	if (p1 == "" && p2 == "") { return true; } else { return false; }
    }.property('pass1', 'pass2'),
    match: function() {
	return this.get('pass1') == this.get('pass2');
    }.property('pass1', 'pass2'),
    bad: function() {
	return !(this.get('match') && !this.get('empty'));
    }.property('match', 'empty')
});

App.FadeInView = Ember.View.extend({
    didInsertElement: function(){	
        this.$().hide().fadeIn('slow');
	this.$("p").position({
	    of: this.$(),
	    my: "center center",
	    at: "center center" });
    }
});

App.lowpan = Ember.Object.create({
    url: null,
    apikey: null,
    save: function() {
	console.log("lowpan save");
	console.log(this.get('url') + this.get('apikey'));
	this.checkAPI();
	$.ajax({
	    url: "settings/lowpan",
	    type: "POST",
	    dataType: "json",
	    contentType: "application/json",
	    data: JSON.stringify({
		"url": this.get('url'),
		"password": this.get('apikey')
	    }),
	    success: function(data) {
		App.password.set('ChangeWait', false);
		App.password.set('pass1','');
		App.password.set('pass2','');
	    }
	});
    },
    checkAPI: function () {
	console.log("check api called");
	$.ajax({
	    url: this.get('url'),
	    type: 'GET',
	    dataType: "json",
	    data: { apikey: this.get('apikey') },
	    success: function(data) {
		console.log(data);
	    }
	});
    },
    apiok: false,
});

