// One line 'hack' to extract parameters from url
var params = _.object(_.compact(_.map(location.search.slice(1).split('&'), function(item) {  if (item) return item.split('='); })));

$('document').ready(function() {
  $.ajaxSetup({ timeout: 10000});
  var stewardTemplate = _.template($("#steward-template").html());
  var submissionTemplate = _.template($("#submission-template").html());

  if ("submission" in params) {
    $.getJSON("/submissions/" + params.submission, function(result) {
			$("#title").html("Submission");
      $("#submission").html(submissionTemplate({multihash: params.submission,
        fields: result.submission.fields, files: result.submission.files}));
    })
    .error(function() { 
      $("#submission").html(submissionTemplate({multihash: "Unable to find " + params.submission,
        fields: [], files: []}));
    });
  } else {
    $.getJSON("/stewards/" + params.steward, function(result) {
			$("#title").html("Steward");
      $("#steward").html(stewardTemplate({address: params.steward, steward: result.steward}));
    })
    .error(function() { 
      $("#steward").html(stewardTemplate(
        {address: params.steward, steward: {domain: "Unable to resolve " + params.steward, peers: [], submissions: []}}));
    });
  }
});
