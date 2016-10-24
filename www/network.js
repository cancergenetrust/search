function draw_network(stewards) {

  var addresses = _.keys(stewards);
  var links = [];
  for (var i=0; i < addresses.length; i++) {
    var peers = stewards[addresses[i]]._source.peers;
    for (var j=0; j < peers.length; j++) {
      // Make sure source and destintation exist
      if (!(addresses[i] in stewards)) {
        console.log("Missing steward " + addresses[i]);
      } else if (!(peers[j] in stewards)) {
        console.log("Missing steward " + peers[j]);
      } else {
        links.push({source: stewards[addresses[i]], 
          target: stewards[peers[j]], value: 1.0});
      }
    }
  }

  var svg = d3.select("body").append("svg");

  var force = d3.layout.force()
    .nodes(_.values(stewards))
    .links(links)
    .linkDistance(120)
    .charge(-900)
    .on("tick", tick)
    .start();


  // build the arrow.
  svg.append("svg:defs").selectAll("marker")
    .data(["end"])      // Different link/path types can be defined here
    .enter().append("svg:marker")    // This section adds in the arrows
    .attr("id", String)
    .attr("viewBox", "0 -5 10 10")
    .attr("refX", 15)
    .attr("refY", -1.5)
    .attr("markerWidth", 10)
    .attr("markerHeight", 10)
    .attr("orient", "auto")
    .append("svg:path")
    .attr("d", "M0,-5L10,0L0,5");

  // add the links and the arrows
  var path = svg.append("svg:g").selectAll("path")
    .data(force.links())
    .enter().append("svg:path")
  //    .attr("class", function(d) { return "link " + d.type; })
    .attr("class", "link")
    .attr("marker-end", "url(#end)");

  // define the nodes
  var node = svg.selectAll(".node")
    .data(force.nodes())
    .enter().append("g")
    .attr("class", "node")
    .call(force.drag);

  // add the nodes
  node.append("circle")
    .attr("r", 16)
    .on("click", function(e) {
      if (d3.event.defaultPrevented) return; // skip if drag
      window.location.href = "/cgtd/index.html?steward=" + e._id;
    });

  // add the text 
  node.append("text")
    .attr("x", 18)
    .attr("dy", ".35em")
    .text(function(d) { return d._source.domain.toLowerCase(); });
  node.append("text")
    .attr("x", 0)
    .attr("dy", ".35em")
    .attr("text-anchor", "middle")
    .text(function(d) { return d._source.submissions.length; });

  // add the curvy lines
  function tick() {
    path.attr("d", function(d) {
      var dx = d.target.x - d.source.x,
        dy = d.target.y - d.source.y,
        dr = Math.sqrt(dx * dx + dy * dy);
      return "M" + 
        d.source.x + "," + 
        d.source.y + "A" + 
        dr + "," + dr + " 0 0,1 " + 
        d.target.x + "," + 
        d.target.y;
    });

    node.attr("transform", function(d) { 
      return "translate(" + d.x + "," + d.y + ")"; 
    });
  }

  resize();
  d3.select(window).on("resize", resize);

  function resize() {
    width = window.innerWidth, height = window.innerHeight;
    svg.attr("width", width).attr("height", height);
    force.size([width, height]).resume();
  }
}
