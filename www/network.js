function draw_network(stewards) {
  var cy = cytoscape({
    container: document.getElementById('network'),
    style: [
      {
        selector: 'node',
        style: {
          'content': 'data(id)',
          'text-opacity': 0.9,
          'text-valign': 'center',
          'text-halign': 'center',
          'text-wrap': 'wrap',
          'text-transform': 'lowercase',
          'text-margin-y': '8px',
          'background-color': '#11479e',
          'background-opacity': 0.5,
          label: 'data(label)'
        }
      },
      {
        selector: 'edge',
        style: {
          'width': 4,
          'target-arrow-shape': 'triangle',
          'line-color': '#9dbaea',
          'target-arrow-color': '#9dbaea',
          'curve-style': 'bezier'
        }
      }
    ],
  });


  var addresses = _.keys(stewards);
  for (var i=0; i < addresses.length; i++) {
    cy.add({data: {id: addresses[i],
      label: stewards[addresses[i]]._source.submissions.length + "\n" +
      stewards[addresses[i]]._source.domain}});
  }

  for (var i=0; i < addresses.length; i++) {
    var peers = stewards[addresses[i]]._source.peers;
    for (var j=0; j < peers.length; j++) {
      cy.add({data: {id: 'edge' + i + j, source: addresses[i], target: peers[j]}});
    }
  }

  cy.layout({
    name: 'dagre'
  });

  cy.on('tap', 'node', function(event) {
    window.location.href = "/cgtd/index.html?steward=" + this.data("id");
  });
}

$('document').ready(function() {
  var resultsTemplate = _.template($("#results-template").html());

  $("#query").focus();

  $("#search").submit(function(event) {
    query = $("#query").val(); 
		var request = {
        "query": {
            "match": {
                "_all": {
                    "query": query,
                    "operator": "and"
                }
            }
        },
        "size": 100 
    }
		$.ajax({ 
			url: "/es/cgt/submission/_search", 
			type: "POST", 
			dataType: "json", 
			data: JSON.stringify(request), 
			success: function(results) {
				console.log(results);
				$("#network").hide();
				$("#results").html(resultsTemplate({results: results}));
			}
		}); 
    event.preventDefault();
    ga('send', 'event', 'submissions', 'search', query);
	});

  $.ajax({ 
    url: "/es/cgt/steward/_search/?size=1000", 
    type: "GET", 
    error: function(error) { alert("Search index error, likely undergoing maintenance."); },
    success: function(results) {
      if (results.hits.total == 0) {
        alert("Search index empty, likely undergoing maintenance.");
      } else {
        draw_network(_.indexBy(results.hits.hits, '_id'));
      }
    }
  });
});
