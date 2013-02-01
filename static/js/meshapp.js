var App = Em.Application.create({
    ready: function () { console.log('ready'); App.init()},
});

App.randomMeshAction = function() {
    setTimeout(App.randomMeshAction, 500 + Math.floor(Math.random()*1500));
		if (nodes.length > 8 ) {
				removeNode(nodes[0].eui);
				return;
		}
    var ran = Math.floor(Math.random()*5)
    if (ran == 1) {
				// node
				ran = Math.floor(Math.random()*7)
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
				ran = Math.floor(Math.random()*7)
				if (ran > 1) {
						// add edge
						console.log("add edge");
						var e = {};
						e.etx = Math.floor(Math.random()*4);
						var s = Math.floor(Math.random()*nodes.length);
						e.source = nodes[s];
						var t = s;
						while (t == s) {
								console.log('.');
								t = Math.floor(Math.random()*nodes.length);
						}
						console.log(s)
						console.log(t)	    
						e.target = nodes[t];
						ran = Math.floor(Math.random()*4)
						if (ran == 1) {
								e.pref = true;
						} else {
								e.pref = false;
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
    setTimeout(App.randomMeshAction, 1000);
    addNode({"eui":"a"});
    addNode({"eui":"b"});
    addNode({"eui":"c"});
    addNode({"eui":"d"});

    addEdge({"etx": 2, "source": nodes[0], "target": nodes[1]});
    addEdge({"etx": 2, "source": nodes[0], "target": nodes[2]});
    addEdge({"etx": 2, "source": nodes[0], "target": nodes[3]});
};

