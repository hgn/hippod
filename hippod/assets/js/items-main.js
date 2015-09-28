



function activaTab(tab){
    $('.nav-tabs a[href="#' + tab + '"]').tab('show');
};


var item_data = null;

function ObjectData() {

	this.read = function (item) {
		this.title          = item['object-item'].title;
		this.version        = item['object-item'].version;
		this.categories     = item['object-item']['categories'];
		this.maturity_level = item['object-item']['maturity-level'].level;

		var references, replaces, responsible, tags;

		if (item['object-attachment']) {
			$.each(item['object-attachment'], function(i, data) {
				if (i == 'references') {
					references =  data;
				}
				if (i == 'replaces') {
					replaces = data;
				}
				if (i == 'responsible') {
					responsible = data;
				}
				if (i == 'tags') {
					tags = data;
				}
			});
		}

		this.references = references;
		this.replaces = replaces;
		this.responsible = responsible;
		this.tags = tags;

		if (item['object-achievements']) {
			$.each(item['object-achievements'], function(i, data) {
				if (i == 'date-added') {
				}
				if (i == 'id') {
				}
				if (i == 'test-date') {
				}
				if (i == 'test-result') {
				}
			});
		}
	}

	this.htmlize = function () {
		var buf = "<li><div class=\"panel panel-default\">";
		buf += "<div class=\"panel-body\">";
		buf += "<div class=\"panel-info\">";
		buf += "<p>";
		buf += this.title;
		buf += "</p>";
		buf += this.version + "<br />";
    buf += "</div>";
    buf += "</div>";
    buf += "</div>";
		return buf;
  }
}

function displayItemData() {
      var buf = "";
      $.each(item_data, function(i, item) {
				objectData = new ObjectData();
				objectData.read(item);
				//console.log(objectData);
				buf += objectData.htmlize() + "<br />\n";
      });
      $("#fooooo").html(buf);

		  buf = "";
			buf += "Number of Items to display: " + item_data.length + "<br />";
      $("#items-statistic").html(buf);
}

var obj = { "ordering": "by-submitting-date-reverse", "limit": 50 }

function loadItemData() {
  var query_url = "/api/v1/objects";
	$.ajax({
    contentType: 'application/json; charset=utf-8',
		type: "POST",
		url: query_url,
		dataType: 'json',
		data: JSON.stringify(obj),
    processData: false,
		

		error: function(data){
			alert("Cannot fetch item data" + data);
			//console.log(data);
		},
		success: function(data){
			item_data = data.data;
			displayItemData();
		}
	})
}

$(document).ready(function() {
    activaTab('tab1');
    loadItemData();
});
