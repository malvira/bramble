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
}

App.radio = Ember.Object.create ({
    firmware: null,
    resetcmd: null,
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
	console.log('reload');
	$.ajax({
	    url: "radio/reload",
	    type: "POST",
	    dataType: "json",
	    contentType: "application/json",
	    data: null,
	    success: function(data) {
	    }
	});
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