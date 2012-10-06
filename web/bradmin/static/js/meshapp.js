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
		if ('routes' in data.event) {
		    data.event.routes.forEach( function(item) {
			console.log(item);
//			window.sys.addNode('0212740100010101', {alone:true, mass:.25});
//			window.sys.addNode('br', {alone:true, mass:.25}) // TODO: set the address of the BR root properly
//			window.sys.addNode(item, {alone:true, mass:.25})
		    });
		}
		if ('rank' in data.event) {
		    window.sys.addNode(data.event.src, {mass:.5});
		    console.log(data.event.src);
		    console.log(data.event.rank);
		}
		if ('adr' in data.event) {
		    var src = window.sys.getNode(data.event.src);
		    if (null == src) { window.sys.addNode(window.sys.addNode(data.event.src, {mass:.25})) }
		    var adr = window.sys.getNode(data.event.src);
		    if (null == adr) { window.sys.addNode(window.sys.addNode(data.event.adr, {mass:.25})) }
		    
		    var d = new Date();
		    var edges = window.sys.getEdges(data.event.src, data.event.adr);
		    var edge = edges[0];
		    console.log(edge)
		    if (null != edge) {
			console.log(edge);
			edge.data.time = d.getTime();
			edge.data.etx = data.event.etx/128;
		    } else {
			window.sys.addEdge(data.event.src, data.event.adr, 
					   { etx: data.event.etx/128, 
					     time: d.getTime(), 
					     pref: data.event.pref });
		    }
		}
	    };
	};
    };
};
