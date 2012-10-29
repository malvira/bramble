var App = Em.Application.create({
    ready: function () { console.log('ready'); App.init()},
    channel: null,
    pollCount: 0,
});

App.init = function() {
    App.poll();
};

App.nodes = Em.ArrayController.create({
    content: [],
    addIfNew: function(n) {
	if (this.findProperty('eui', n.eui) == null) {
	    this.pushObject(n);	
	    var c = this.get('content');
	    c.sort(function(a,b) {
		return a.eui - b.eui;
	    });
	    this.replace(0,c.length,c);
	}},

});

App.node = Em.Object.extend({
    eui: null,
});

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
		    });
		}
		if ('rank' in data.event) {
		    var node = {};
		    node.eui = data.event.src;
		    node.rank = data.event.rank;
		    n = App.node.create({ eui: node.eui, rank: node.rank });
		    App.nodes.addIfNew(n);
		    window.addNode(node);
		}
		if ('adr' in data.event) {
		    var src = {};
		    var target = {};
		    src.eui = data.event.src;
		    target.eui = data.event.adr;
		    window.addNode(src);
		    window.addNode(target);
		    
		    s = App.node.create({ eui: src.eui })
		    t = App.node.create({ eui: target.eui })
		    App.nodes.addIfNew(s)
		    App.nodes.addIfNew(t)

		    var d = new Date();
		    var edge = {};
		    edge.time = d.getTime();
		    edge.etx = data.event.etx/128;
		    edge.source = data.event.src;
		    edge.target = data.event.adr;
		    edge.pref = data.event.pref;
		    window.addEdge(edge);
		}
	    };
	};
    };
};

App.viewInfoMesh = Ember.View.extend({
    nodeBinding: 'App.nodes',
});

