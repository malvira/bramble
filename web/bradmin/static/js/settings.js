console.log('settings.js');

var App = Em.Application.create({
    ready: function () { console.log('ready'); App.init()},
    passChangeWait: false,
    passChangeState: 'none',
    pass1: "",
    pass2: "",
    changepass: function() { 
	if(this.get('pass1') == this.get('pass2'))
	{
	    this.set('passChangeWait', true);
	    $.ajax({  
		url: "settings/newpass",  
		type: "POST",  
		dataType: "json",  
		contentType: "application/json",  
		data: JSON.stringify({ "password": this.get('pass1') }),  
		success: function(data) {
		    console.log('pass change ok');
		    App.set('passChangeWait', false);
		    App.set('pass1','');
		    App.set('pass2','');
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
    passbad: function() {
	return !(this.get('match') && !this.get('empty'));
    }.property('match', 'empty')
});

App.FadeInView = Ember.View.extend({
    didInsertElement: function(){	
        this.$().hide().fadeIn('slow');
    }
});


/* try using find, addObject, and removeObject instead to manage the pings */

/* initialization */
App.init = function() {
    App.tick.settimer();
}

App.ChangePass = function(pass1, pass2) {
    console.log('called change pass');
    console.log(pass1);
    console.log(pass2);



}

/* debug views */
App.tick = Ember.Object.create({
    settimer: function () { setInterval(function() { App.tick.set('tick',App.tick.tick+1); }, 1000); },
    tick: 0,
    foo: "",
    bar: function() {
	console.log('bar');
	return this.get('foo');
    }.property('foo')
});

App.DebugView = Em.View.extend({
    tickBinding: 'App.tick.tick',
    fooBinding: 'App.tick.foo',
    barBinding: 'App.tick.bar'
});


