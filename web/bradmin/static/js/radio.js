console.log('settings.js');

var App = Em.Application.create({
    ready: function () { console.log('ready'); App.init()},
});

App.init = function() {    
    $.ajax({
	url: "radio/radio",  
	type: "GET",  
	dataType: "json",  
	contentType: "application/json",  
	success: function(data) {
	    App.radio.set('firmware', data.firmware);
	    App.radio.set('resetcmd', data.resetcmd);
	}
    });  
    $.ajax({
	url: "radio/tunslip",  
	type: "GET",  
	dataType: "json",  
	contentType: "application/json",  
	success: function(data) {
	    App.tunslip.set('address', data.address);
	    App.tunslip.set('device', data.device);
	    App.tunslip.set('baud', data.baud);
	}
    });  

    App.mainView.append();

    App.statusSocket = io.connect('/status');
    App.statusSocket.on('radio', function(data) {
	d = JSON.parse(data);
	console.log("radio " + data);
	console.log(d);
	if (d.hasOwnProperty("loadRadioProgress")) {
	    App.mainView.set('progress', d.loadRadioProgress)
	}
	if (d.hasOwnProperty("task")) {
	    App.mainView.set('task', d.task);
	}
    });

};


Ember.Handlebars.registerHelper('trigger', function (evtName, options) {

    var options = arguments[arguments.length - 1],
    hash = options.hash,
    view = options.data.view,
    target;

    view = view.get('concreteView');

    if (hash.target) {
        target = Ember.Handlebars.get(this, hash.target, options);
    } else {
        target = view;
    }

    Ember.run.next(function () {
        target.trigger(evtName);
    });
});

/* this has one big monolithic view to do everything */
/* someday should rewrite this to be more ember-ish */
App.mainViewClass = Ember.View.extend({
    templateName: 'main',
    doToolTips: function () {
	$('#tunslip-tip').qtip({content: "The fallback address will be use if an ipv6 address cannot be established"});
    },
    /* keep track of what we are doing */
    /* tasks are: idle, changingChannel, uploadingFirmware, reloadingFirmware */
    task: "idle",
    progress: "100%", /* current progress in the task */
    progressStyle: function() {
	return "width: " + this.get('progress') + "; visibility: " + this.get('progressVisible') + ";";
    }.property('progress'),
    progressVisible: function() {
	if (this.get('doingSomething')) {
	    return "visible";
	} else {
	    return "hidden";
	}
    }.property('doingSomething'),
    doingSomething: function() {
	if (this.get('task') != 'idle') { 
	    return true; 
	} else  {
	    return false;
	}
    }.property('task'),
});



App.mainView = App.mainViewClass.create();

App.radio = Ember.Object.create ({
    channels: [11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26],
    newChannel: null,
    oldChannel: null,
    firmware: null,
    resetcmd: null,
    changeChannel: function () {
	console.log("change channel");
	if (this.get('newChannel') != this.get('oldChannel')) {
	    App.mainView.set('task', 'changingChannel');
	    console.log("setting new channel")
	    $.ajax({
		url: "radio/channel",
		type: "POST",
		context: this,
		contentType: "application/json",
		data: JSON.stringify({
		    "channel": this.get('newChannel'),
		}),
		success: function(data) {
		    this.set('oldChannel', this.get('newChannel'));
		    App.mainView.set('task','idle');
		}
	    });
	}	
    },
    channelChangeOk: function () {
	return this.get('newChannel') != this.get('oldChannel');
    }.property('newChannel', 'oldChannel'),
    save: function() {
	$.ajax({
	    url: "radio/radio",
	    type: "POST",
	    dataType: "json",
	    contentType: "application/json",
	    data: JSON.stringify({
		"firmware": this.get('firmware'),
		"resetcmd": this.get('resetcmd')
	    }),
	    success: function(data) {
	    }
	});
    },
    reload: function() {
	App.mainView.set('task', 'reloadingFirmware');
	console.log('reload');
	$.ajax({
	    url: "radio/reload",
	    type: "POST",
	    dataType: "json",
	    contentType: "application/json",
	    data: null,
	    success: function(data) {
		App.mainView.set('task', 'idle');
	    }
	});
    },
    factoryRestore: function() {
	App.statusSocket.emit("radio", "doFactoryRestore");
	App.mainView.set('task', 'factoryRestore');
    }
});

App.tunslip = Ember.Object.create ({
    address: null,
    device: null,
    baud: null,
    save: function() {
	$.ajax({
	    url: "radio/tunslip",
	    type: "POST",
	    dataType: "json",
	    contentType: "application/json",
	    data: JSON.stringify({
		"address": this.get('address'),
		"device": this.get('device'),
		"baud": this.get('baud')
	    }),
	    success: function(data) {
	    }
	});
    }
});

App.preset = Ember.Object.create ({
    br12: function () {
	App.radio.set('resetcmd','mcreset');
	App.tunslip.set('address','aaaa::1/64');
	App.tunslip.set('device','/dev/ttyS0');
	App.tunslip.set('baud','115200');
	App.radio.save();
	App.tunslip.save();
    },
    econotag: function () {
	App.radio.set('resetcmd','bbmc -l redbee-econotag reset');
	App.tunslip.set('address','aaaa::1/64');
	App.tunslip.set('device','/dev/ttyUSB1');
	App.tunslip.set('baud','115200');
	App.radio.save();
	App.tunslip.save();
    },
    cooja: function () {
	App.radio.set('resetcmd','');
	App.tunslip.set('address','aaaa::1/64');
	App.tunslip.set('device','');
	App.tunslip.set('baud','');
	App.radio.save();
	App.tunslip.save();
    },
});