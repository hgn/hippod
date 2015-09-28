
// pBytes: the size in bytes to be converted.
// pUnits: 'si'|'iec' si units means the order of magnitude is 10^3, iec uses 2^10
function prettyNumber(pBytes, pUnits) {
    // Handle some special cases
    if(pBytes == 0) return '0 Bytes';
    if(pBytes == 1) return '1 Byte';
    if(pBytes == -1) return '-1 Byte';

    var bytes = Math.abs(pBytes)
    if(pUnits && pUnits.toLowerCase() && pUnits.toLowerCase() == 'si') {
        // SI units use the Metric representation based on 10^3 as a order of magnitude
        var orderOfMagnitude = Math.pow(10, 3);
        var abbreviations = ['Bytes', 'kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    } else {
        // IEC units use 2^10 as an order of magnitude
        var orderOfMagnitude = Math.pow(2, 10);
        var abbreviations = ['Bytes', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB'];
    }
    var i = Math.floor(Math.log(bytes) / Math.log(orderOfMagnitude));
    var result = (bytes / Math.pow(orderOfMagnitude, i));

    // This will get the sign right
    if(pBytes < 0) {
        result *= -1;
    }

    if(result >= 99.995 || i==0) {
        return result.toFixed(0) + ' ' + abbreviations[i];
    } else {
        return result.toFixed(2) + ' ' + abbreviations[i];
    }
}


function activaTab(tab){
    $('.nav-tabs a[href="#' + tab + '"]').tab('show');
};

function loadRessourceData() {
  var res_url = "/api/v1.0/resources";
	$.ajax({
		type: "GET",
		url: res_url,
		error: function(data){
			$("#error-dialog").modal();
		},
		success: function(data){
			//$(target).html(data);
            var buf = "";
            if (data['data'] && data['data']['overall']) {
                var overall = data['data']['overall'];
                buf += "Memory usage of Database: " + prettyNumber(overall, 'iec') + "<br />\n";
                //buf += "Memory usage of Database: " + overall + " byte<br />\n";
            }
            /*
                $.each(data, function(i, item) {
                    $("#data-usage").append("xxx");
                    buf += "part: " + i + " " + item + "byte<br />\n";
                });
            */
            $("#usage-data").html(buf);
		}
	})
}


$(document).ready(function() {
  activaTab('tab1');

	loadRessourceData();

});

