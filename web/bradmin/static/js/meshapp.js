var App = Em.Application.create({
    ready: function () { console.log('ready'); App.init()},
    channel: null,
    pollCount: 0,
});

/* try using find, addObject, and removeObject instead to manage the pings */

/* initialization */
App.init = function() {
    App.poll();
}

App.getChan = function() {
    $.ajax({  
	url: "channel",  
	type: "POST",  
	dataType: "json",  
	contentType: "application/json",  
	data: JSON.stringify({ "events": ["brsChanged", "ping"] }),  
	success: function(data) {
	    App.set('channel', data.channel);
	    App.poll();
	}
    });  
}

App.poll = function () {
    if (App.get('pollCount') == 0) {
	if(App.get('channel') == null) {
	    App.getChan();	    
	} else {
	    App.set('pollCount', App.pollCount + 1);
	    $.ajax({  
		url: "channel/" + App.get('channel'),  
		type: "GET",  
		dataType: "json",  
		success: function(data) {
		    App.set('pollCount', App.pollCount - 1);
		    App.doChanData(data);
		    App.poll();
		},
		error: function(xhr, status, err) {
		    App.set('pollCount', App.pollCount - 1);
		    if(status == 'error') {
			setTimeout( function() { App.set('channel', null); App.poll(); }, 15000);
		    } else {
			App.poll();
		    }
		}
	    });  
	}
    } else {
	setTimeout( function() { App.poll(); }, 15000);
    }
};    

App.doChanData = function(data) {
    if (data != null) {
	if ('event' in data) {
	    if (data.event.name == 'rplData') {
		data.event.routes.forEach( function(item) {
		    window.sys.addNode('br', {alone:true, mass:.25}) // TODO: set the address of the BR root properly
		    window.sys.addNode(item, {alone:true, mass:.25})
		});
	    };
	};
    };
};
