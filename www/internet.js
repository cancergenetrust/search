$('document').ready(function() {
	$('#query').keypress(function(event){
		var keycode = (event.keyCode ? event.keyCode : event.which);
		if(keycode == '13'){
      $.getJSON("/es/_search?q=" + $(this).val(), function(results) {
        console.log(results);
        if (results.hits.total > 0) {
          window.open("/cgtd/index.html?submission=" + results.hits.hits[0]._id);
        }
      });
		}
	});

	$("#progressDialog").modal("show");
	$("#progress").html("Finding and authenticating stewards...");
	// $.getJSON("/cgtd/v0/stewards", function(stewards) {
	// $.getJSON("/stewards_temp.json", function(stewards) {
  $.getJSON("/es/cgt/steward/_search/?size=15", function(results) {
		$("#progressDialog").modal("hide");
		if (results.hits.total == 0) {
			alert("No stewards found");
		} else {
			var cy = cytoscape({
				container: document.getElementById('cy'),
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

			let addresses = _.keys(stewards);
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
				window.open("/cgtd/index.html?steward="+this.data("id"));
			});
		}
	});
});
