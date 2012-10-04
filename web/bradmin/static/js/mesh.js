//
//  main.js
//
//  A project template for using arbor.js
//

(function($){

    var Renderer = function(raph, elt){
	var canvas = elt;
      var r;
      var particleSystem;

    var that = {
      init:function(system){
//          $(window).resize(that.resize);
          particleSystem = system;
	  particleSystem.screenSize(620, 420);
          particleSystem.screenPadding(80); // leave an extra 80px of whitespace per side
          that.initMouseHandling();
//	  that.resize();
          r = raph;
      },
	
      redraw:function(){
        // 
        // redraw will be called repeatedly during the run whenever the node positions
        // change. the new positions for the nodes can be accessed by looking at the
        // .p attribute of a given node. however the p.x & p.y values are in the coordinates
        // of the particle system rather than the screen. you can either map them to
        // the screen yourself, or use the convenience iterators .eachNode (and .eachEdge)
        // which allow you to step through the actual node objects but also pass an
        // x,y point in the screen's coordinate system
        // 

	  var w = 640 * .01;

          r.clear();

          particleSystem.eachEdge(function(edge, pt1, pt2){
              // edge: {source:Node, target:Node, length:#, data:{}}
              // pt1:  {x:#, y:#}  source position in screen coords
              // pt2:  {x:#, y:#}  target position in screen coords
	      var light = 1 - (1 / edge.data.etx) * .5;
	      if (edge.data.etx == 0 ) { light = .5; }
	      if (light > .97) { light = .97; }

	      if (edge.data.time) {
		  var now = new Date();
		  var sat = 1 - (now.getTime() - edge.data.time)/(1000*60);
		  if (sat < 0 ) { sat = 0; }
	      } else {
		  sat = .001;
	      }

	      r.path([["M", pt1.x, pt1.y], ["L", pt2.x, pt2.y]]).attr({stroke: Raphael.hsl(.6, sat, light), "stroke-width": "2"});
          })

	  particleSystem.eachNode(function(node, pt) {
              // node: {mass:#, p:{x,y}, name:"", data:{}}
              // pt:   {x:#, y:#}  node position in screen coords
	      r.circle(pt.x,pt.y,w).attr({fill: "white"});
	  })

      },

      resize:function(){   
	  console.log($(canvas).width());
	  console.log($(window).height());
          particleSystem.screenSize($(canvas).width(), $(window).height());
          r.setSize($(canvas).width(), $(window).height());
          that.redraw();
      },
      
      initMouseHandling:function(){
        // no-nonsense drag and drop (thanks springy.js)
        var dragged = null;

        // set up a handler object that will initially listen for mousedowns then
        // for moves and mouseups while dragging
        var handler = {
          clicked:function(e){
            var pos = $(canvas).offset();
            _mouseP = arbor.Point(e.pageX-pos.left, e.pageY-pos.top)
            dragged = particleSystem.nearest(_mouseP);

            if (dragged && dragged.node !== null){
              // while we're dragging, don't let physics move the node
              dragged.node.fixed = true
            }

            $(canvas).bind('mousemove', handler.dragged)
            $(window).bind('mouseup', handler.dropped)

            return false
          },
          dragged:function(e){
            var pos = $(canvas).offset();
            var s = arbor.Point(e.pageX-pos.left, e.pageY-pos.top)

            if (dragged && dragged.node !== null){
              var p = particleSystem.fromScreen(s)
              dragged.node.p = p
            }

            return false
          },

          dropped:function(e){
            if (dragged===null || dragged.node===undefined) return
            if (dragged.node !== null) dragged.node.fixed = false
            dragged.node.tempMass = 1000
            dragged = null
            $(canvas).unbind('mousemove', handler.dragged)
            $(window).unbind('mouseup', handler.dropped)
            _mouseP = null
            return false
          }
        }
        
        // start listening
        $(canvas).mousedown(handler.clicked);

      },
      
    }

    // helpers for figuring out where to draw arrows (thanks springy.js)
    var intersect_line_line = function(p1, p2, p3, p4)
    {
      var denom = ((p4.y - p3.y)*(p2.x - p1.x) - (p4.x - p3.x)*(p2.y - p1.y));
      if (denom === 0) return false // lines are parallel
      var ua = ((p4.x - p3.x)*(p1.y - p3.y) - (p4.y - p3.y)*(p1.x - p3.x)) / denom;
      var ub = ((p2.x - p1.x)*(p1.y - p3.y) - (p2.y - p1.y)*(p1.x - p3.x)) / denom;

      if (ua < 0 || ua > 1 || ub < 0 || ub > 1)  return false
      return arbor.Point(p1.x + ua * (p2.x - p1.x), p1.y + ua * (p2.y - p1.y));
    }

    var intersect_line_box = function(p1, p2, boxTuple)
    {
      var p3 = {x:boxTuple[0], y:boxTuple[1]},
          w = boxTuple[2],
          h = boxTuple[3]

      var tl = {x: p3.x, y: p3.y};
      var tr = {x: p3.x + w, y: p3.y};
      var bl = {x: p3.x, y: p3.y + h};
      var br = {x: p3.x + w, y: p3.y + h};

      return intersect_line_line(p1, p2, tl, tr) ||
            intersect_line_line(p1, p2, tr, br) ||
            intersect_line_line(p1, p2, br, bl) ||
            intersect_line_line(p1, p2, bl, tl) ||
            false
    }

    return that
  }    

  $(document).ready(function(){
      window.sys = arbor.ParticleSystem(1000, 600, 0.5); // create the system with sensible repulsion/stiffness/friction
      var sys = window.sys;
      var raph = Raphael("mesh", 620, 420),
                    discattr = {fill: "#fff", stroke: "none"};

    sys.parameters({gravity:true}) // use center-gravity to make the graph settle nicely (ymmv)
      sys.parameters({dt:0.002})
    
      sys.renderer = Renderer(raph, "#mesh") // our newly created renderer will have its .init() method called shortly by sys...


      // add some nodes to the graph and watch it go...
      var now = new Date();
//      sys.addEdge('a','b', {etx: 1, time: now.getTime()});
//      sys.addEdge('a','c', {etx: 2, time: now.getTime() - 1000 * 60 * 60});
//      sys.addEdge('a','d', {etx: 4, time: now.getTime() - 1000 * 60 * 60 * 24});
//      sys.addEdge('a','e', {etx: 8});
//      sys.addEdge('e','f', {etx: 200});
//      sys.addEdge('e','g', {etx: 15});
//    sys.addNode('f', {alone:true, mass:.25});

    // or, equivalently:
    //
    // sys.graft({
    //   nodes:{
    //     f:{alone:true, mass:.25}
    //   }, 
    //   edges:{
    //     a:{ b:{},
    //         c:{},
    //         d:{},
    //         e:{}
    //     }
    //   }
    // })
    
  })

})(this.jQuery)