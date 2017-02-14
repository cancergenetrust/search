$('document').ready(function() {
  var resultsTemplate = _.template($("#results-template").html());

  $("#query").focus();

  $("#search").submit(function(event) {
    $.ajax({ 
      url: "/submissions/search?query=" + encodeURIComponent($("#query").val()), 
      type: "GET", 
      dataType: "json", 
      success: function(results) {
        $("svg").hide();
        $("#results").html(resultsTemplate({results: results}));
        var data = "text/json;charset=utf-8,"
          + encodeURIComponent(JSON.stringify({
            query: query,
            submissions: _.pluck(results.hits.hits, "_id")}));
        $("#download").attr("href", "data:" + data);
      }
    }); 
    event.preventDefault();
    ga('send', 'event', 'submissions', 'search', query);
  });

  $.ajax({ 
    url: "stewards", 
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
