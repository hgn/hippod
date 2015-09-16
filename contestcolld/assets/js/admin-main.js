$(document).ready(function() {


  var res_url = "/api/v1.0/resources";

	$.ajax({
		type: "GET",
		url: res_url,
		error: function(data){
			$("#error-dialog").modal();
		},
		success: function(data){
			//$(target).html(data);
      var buf = ""
      $.each(data, function(i, item){
          $("#data-usage").append("xxx");
          buf += "part: " + i + " " + item + "byte<br />\n";
      });
      $("#usage-data").html(buf);
		}
	})
});

