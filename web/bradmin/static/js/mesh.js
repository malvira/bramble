
var nodeToIdx = {};
var linkToIdx = {};

window.addNode = function(node) {
    if ( nodeToIdx.hasOwnProperty(node.eui) ) {
	/* treat this as an update */
    } else {
	/* new node */
	nodeToIdx[node.eui] = nodes.length;
	nodes.push(node);
    }
    updateMesh();
};

window.addEdge = function(edge) {
    var key = edge.source + "->" + edge.target;
    if ( linkToIdx.hasOwnProperty(key) ) {
	/* update a link */
    } else {
	/* new link */
	linkToIdx[key] = links.length;
	edge.source = nodeToIdx[edge.source];
	edge.target = nodeToIdx[edge.target];
	links.push(edge);
    }
    updateMesh();
};

$(window).resize(function() {
    window.force.size([$("#mesh").width(), $(window).height()]);
    $("#mesh").height($(window).height());
    window.force.resume();
});

function updateMesh() {

    link = svg.selectAll(".link")
	.data(links)
	.enter().insert("line", ".node")
	.order()
	.attr("class", "link");

    node = svg.selectAll(".node")
    	.data(nodes)
    	.enter().append("circle")
	.order()
    	.attr("class", "node")
    	.attr("r", 10)
	.call(force.drag);
   
    force.start();

}

var svg;
var nodes;
var links;
var force;

(function() {

    $("#mesh").height($(window).height());

    svg = d3.select("#mesh").append("svg")
	.attr("class", "sixteen columns");

    force = d3.layout.force()
	.linkDistance(function(d) { if (d.etx > 1 ) { return d.etx * 50; } else { return 25; }})
	.charge(-100)
	.gravity(0.05)
	.size([$("#mesh").width(), $(window).height()]);

    nodes = force.nodes();
    links  = force.links();

    force.on("tick", function() {
	svg.selectAll(".node")
	    .attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });

	svg.selectAll(".link")
	    .attr("x1", function(d) { return d.source.x; })
	    .attr("y1", function(d) { return d.source.y; })
	    .attr("x2", function(d) { return d.target.x; })
	    .attr("y2", function(d) { return d.target.y; });
    });

    updateMesh();
 
})(); 

