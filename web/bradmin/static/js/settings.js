console.log('settings.js');

var App = Em.Application.create({
    ready: function () { console.log('ready'); App.init()},
    passChangeWait: false,
    passChangeState: 'none',
    changepass: function() { console.log('changepass'); console.log(App.pass1); console.log(App.pass2); console.log(App.match)},
    pass1: "",
    pass2: "",
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

/* try using find, addObject, and removeObject instead to manage the pings */

/* initialization */
App.init = function() {
    App.tick.settimer();
}

App.ChangePass = function(pass1, pass2) {
    console.log('called change pass');
    console.log(pass1);
    console.log(pass2);
    if(pass1 != pass2) {
	App.set('passChangeState', 'different');
    } else {
	App.set('passChangeState', 'wait');
    }
    App.set('passChangeWait', true);
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


