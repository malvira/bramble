var App = Em.Application.create({
    ready: function () { console.log('ready'); App.init()},
    channel: null,
    pollCount: 0,
    brip: null,
    getIP: function() {
				$.ajax({  
						url: "radio/ip",  
						type: "GET",  
						dataType: "json",  
						contentType: "application/json",  
						success: function(data) {
								if(data.status == 'error') { 
										window.setTimeout(App.getIP, 1000); 
										return; 
								}
								try {
										App.set('brip', data.addrs[0]);
										breui = ipv6ToIID(App.get('brip'));
										n = App.node.create({ eui: breui, addr: App.get('brip') });
										App.nodes.addIfNew(n);
										window.addNode(n);
										App.refreshNodes();
								} catch(e) {
										window.setTimeout(App.getIP, 1000); 
								}
						},
						error: function() {
								window.setTimeout(App.getIP, 1000);
						}
				});  
    },
    refreshNodes: function() {	
				if(App.get('brip') == null) { return; }
				$.ajax({  
						url: "/rplinfo/" + App.get('brip') + '/routes',  
						type: "GET",  
						contentType: "application/json",  
						success: function(data) {
								console.log(data);
								routes = data.routes;
								routes.forEach(function(r) {										
										dest = ipv6ToIID(r.dest);										
										n = App.node.create({ eui: dest, addr: r.dest });
										App.nodes.addIfNew(n);
										window.addNode(n);
										n.getParents();		
								});
						}
				});  	
    }
		
});

/* get IID from an ipv6 device */
ipv6ToIID = function(ip) {
    // this is a bit of a hack
    // we want to deal with euis but we get routes back from the border router
    // assume that the IP addresses are derived from the IID and assume the last 64bits
    // also assume the :: isn't in the IID
    elts = ip.split(':');
    // pad each with leading zeros
    ip = elts.slice(elts.length-4,elts.length)
    
    ip.forEach(function(i) {
	var h = parseInt(i, 16);
	this[this.indexOf(i)] = ("0000" + h.toString(16)).substr(-4);
    }, ip);
    
    ip = ip.join('');
    return ip;
}

App.randomMeshAction = function() {
    var ran = Math.floor(Math.random()*3)
    if (ran == 1) {
	// node
	ran = Math.floor(Math.random()*5)
	if (ran > 1) {
	    // add node
	    console.log("add node");
	    var n = {};
	    n.eui = String(Math.floor(Math.random()*32))	    
	    console.log(n);
	    addNode(n);
	} else {
	    // remove node
	    console.log("remove node");
	    var n = nodes[Math.floor(Math.random()*links.length)]
	    console.log(n);
	    if (n) { removeNode(n.eui); }
	}
    } else {
	// edge
	ran = Math.floor(Math.random()*5)
	if (ran > 1) {
	    // add edge
	    console.log("add edge");
	    var e = {};
	    e.etx = Math.floor(Math.random()*4);
	    e.source = nodes[Math.floor(Math.random()*nodes.length)];
	    e.target = nodes[Math.floor(Math.random()*nodes.length)];
	    ran = Math.floor(Math.random()*3)
	    if (ran == 1) {
		e.pref = false;
	    } else {
		e.pref = true;
	    }
	    console.log(e);
	    addEdge(e);
	} else {
	    // remove edge
	    console.log("remove edge");
	    var e = links[Math.floor(Math.random()*links.length)]
	    console.log(e);
	    if (e) { removeEdge(e); }
	}
    }

}

App.init = function() {
    App.nodeListView.appendTo('#list');
    App.nodeDetailsView.appendTo('#details');

    App.getIP();
    setInterval(App.refreshNodes, 10000);
    App.poll();
//    setInterval(App.randomMeshAction, 1000);
};

App.nodes = Em.ArrayController.create({
    content: [],
    addIfNew: function(n) {
	if (this.findProperty('eui', n.eui) == null) {	    
	    this.pushObject(n);
	    if (App.selectedNode == null) { App.set('selectedNode', n); }
	    var c = this.get('content');
	    c.sort(function(a,b) {
		return a.eui - b.eui;
	    });
	    this.replace(0,c.length,c);
	}
    },
});

App.nodeListView = Ember.View.create({
    templateName: 'node-list',
});

App.nodeDetailsView = Ember.View.create({
    templateName: 'node-details',
});

App.nodeItemView = Ember.View.extend({
    classNameBindings: ['content.selected', 'content.focus'],
    template: Ember.Handlebars.compile('{{view.content.eui}}'),
    mouseEnter: function(event, view) {
    	this.content.set('focus', true);
    	this.$().animate({
    	    backgroundColor: "#abcdef"
    	}, 250 );
    },
    mouseLeave:  function(event, view) {
    	this.content.set('focus', false);
    	this.$().animate({
    	    backgroundColor: "#ffffff"
    	}, 75 );	
    },
    click: function(e,v) {
    	this.content.select();
    }
});

App.selectedNode = null;
App.node = Em.Object.extend({
    eui: null,
    addr: null,
    coapURL: function() {
				return "coap://[" + this.get('addr') + "]";
    }.property('addr'),
    selected: false,
    focus: false,
    select: function() {
				if(App.selectedNode) { 
						App.selectedNode.set('selected', false); 
						window.mesh.selectAll("#eui" + App.selectedNode.eui).style("stroke", "black");
				}
				this.set('selected', true);
				App.set('selectedNode', this);
				var eui = App.get('selectedNode').get('eui');
				window.mesh.selectAll("#eui" + eui).style("stroke", "red");
    },
    clearEdges: function() {
				console.log(this.eui + " clear edges");
    },
    getParents: function() {
				var eui = this.eui;
				var n = this
				$.ajax({  
						url: "/rplinfo/" + this.get('addr') + '/parents',  
						type: "GET",  
						dataType: "json",  
						contentType: "application/json",  
						success: function(data) {
								
								console.log(data);
								
								try
								{
										data.parents.forEach(function(p) {
												window.addNode(p);
												n = App.node.create({ eui: p.eui })
												App.nodes.addIfNew(n)
												
												var edge = {};
												edge.etx = p.etx/128;
												edge.source = window.nodeFromEUI(eui);
												edge.target = window.nodeFromEUI(p.eui);
												edge.pref = p.pref;
												window.addEdge(edge);
										});
								}
								catch(e)
								{
										if (data.response == '') {
												// should remove all this nodes edges here
												n.clearEdges();
										} else {
												console.log('invalid json');
												console.log(data.response);
										}
								}
								
						}
				});  
    }
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
    nodeBinding: 'App.nodes'
});

App.nodeItem = Ember.View.extend({
    templateName: 'node-item',
    euiBinding: null,
    selectedBinding: false,
});

App.selectedNodeView = Ember.View.extend({
    nodeBinding: 'App.selectedNode',
});