$('document').ready(function() {
  var resultsTemplate = _.template($("#results-template").html());

  $("#query").focus();

  $("#search").submit(function(event) {
    event.preventDefault();
    $.getJSON("/es/_search?q=" + $("#query").val(), function(results) {
      if (results.hits.total > 0) {
        console.log(results);
        $("#network").hide();
        $("#results").html(resultsTemplate({results: results}));
      }
    });
	});

  $.getJSON("/es/cgt/steward/_search/?size=1000", function(results) {
		if (results.hits.total == 0) {
			alert("No stewards found");
		} else {
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

      stewards = _.indexBy(results.hits.hits, '_id');

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
	});
});
