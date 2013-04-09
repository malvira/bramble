console.log('settings.js');

var App = Em.Application.create({
    ready: function () { console.log('ready'); App.init()},
});

App.init = function() {    

    App.changePassView.appendTo("#changePass");
    App.lowpanAPIView.appendTo("#lowpanAPI");
    App.distroView.appendTo("#distro");
    
    App.distroView.checkForUpdates();

    $.ajax({
	url: "settings/lowpan",  
	type: "GET",  
	dataType: "json",  
	contentType: "application/json",  
	success: function(data) {
	    App.lowpan.set('url', data.url);
	    App.lowpan.set('apikey', data.password);
	    App.lowpan.checkAPI();
	}
    });  
}

App.distroView = Ember.View.create({
    templateName: "distro",
    distro: "",
    release: "",
    url: "",
    haveUpdates: false,
    checkWait: false,
    fullURL: function() {
	return "http://" + this.get('url') + '/' + this.get('distro') + '/' + this.get('release');
    }.property('distro', 'release', 'url'),
    /* perform a check for updates.json */
    /* Access-Control-Allow-Origin: *  must be present in the response or */
    /* the ajax will fail */
    checkForUpdates: function () {
	console.log("checkForUpdates");
//	this.set('checkWait', true); // broken, maybe fixed in newer ember?
	$.ajax({
	    url: this.get('fullURL') + "/updates.json",
	    type: 'GET',
	    dataType: "json",
	    context: this,
	    success: function(data) {
		console.log(data);
//		this.set('checkWait', false);
		this.set('haveUpdates', true);
	    },
	    error: function(data) {
//		this.set('checkWait', false);
		this.set('haveUpdates', false);		
	    }
	});	
    }
});

App.changePassView = Ember.View.create({
    templateName: "passwordView"
});
App.lowpanAPIView = Ember.View.create({
    templateName: "lowpanAPI"
});

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
    saveWait: false,
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
		console.log("save ok");
	    }
	});
    },
    checkAPI: function () {
	console.log("check api called");	
	App.lowpan.set('saveWait', true);
	try {
	    this.set('url',this.get('url').replace(/\s/g, ''));
	    this.set('apikey',this.get('apikey').replace(/\s/g, ''));
	} catch (err) {
	    App.lowpan.set('saveWait', false);
        }
	$.ajax({
	    url: this.get('url'),
	    type: 'GET',
	    dataType: "json",
	    data: { apikey: this.get('apikey') },
	    success: function(data) {
		console.log(data);
		App.lowpan.set('saveWait', false);		
		if(data.status == 'ok') {
		    App.lowpan.set('apiok', true);
		} else { 
		    App.lowpan.set('apiok', false);
		}
	    },
	    error: function(data) {
		App.lowpan.set('saveWait', false);
		App.lowpan.set('apiok', false);		
	    }
	});
    },
    apiok: false,
});

