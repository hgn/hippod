$(document).ready(function() {


  var url = "/api/v1.0/resources";
  $.getJSON(url, function(result){
      //$("#usage-data").empty();
      var buf = ""
      $.each(result, function(i, item){
          $("#data-usage").append("xxx");
          buf += "part: " + i + " " + item + "byte<br />\n";
      });
      $("#usage-data").html(buf);
  });

});
