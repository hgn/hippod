



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
		this.object_id      = item['object-item-id'];

	  this.tags = "-";
	  this.replaces = "-";
	  this.responsible = "Unknown";
	  this.references = "-";

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
					this.date_added  = data;
				}
				if (i == 'id') {
					this.id  = data;
				}
				if (i == 'test-date') {
					this.test_date  = data;
				}
				if (i == 'result') {
					this.result  = data;
				}
			});
		}
	}

	this.getResult = function (item) {
		return this.result
	}

	this.htmlize = function () {
    var buf = '<div class="item-container">';
    buf += '<div class="attachment-result"></div>';
    buf += '<div class="item-data">';
    buf += '<div class="item-container-title">';
    buf += this.title;
    buf += '</div>';
    buf += '<div class="item-data-left">';
    buf += '<div><strong>Last achievement:</strong> ';
    buf += '<span class="glyphicon glyphicon-time" aria-hidden="true"></span> ';
    buf += '4 days ago';
    buf += '</div>';
    buf += '<div><strong>Submitter:</strong> ';
    buf += 'John Doe';
    buf += '</div>';
    buf += '<div><strong>Result:</strong> ';
    buf += '<span class="label label-success">';
    buf += 'passed';
    buf += '</span>';
    buf += '</div>';
    buf += '</div>';
    buf += '<div class="item-data-middle"> ';
    buf += '<div><strong>Tags:</strong> ';
    buf += 'foo, bar, foobar';
    buf += '</div>';
    buf += '<div><strong>References:</strong> ';
    buf += 'ref:03030, ref:0509382, ref:29239';
    buf += '</div>';
    buf += '<div><strong>Responsible:</strong> ';
    buf += this.responsible;
    buf += '</div>';
    buf += '</div>';
    buf += '<div class="item-data-right">';
    buf += '<div><strong>Category:</strong> ';
    buf += this.categories;
    buf += '</div>';
    buf += '<div><strong>ID:</strong> ';
    buf += this.object_id;
    buf += '</div>';
    buf += '<div><strong>Maturity Level:</strong> ';
    buf += '<span class="label label-info">';
    buf += this.maturity_level;
		buf += '</span>';
    buf += '</div>';
    buf += '<div><strong>Version:</strong> ';
    buf += this.version;
    buf += '</div>';
    buf += '</div>';
    buf += '</div>';
    buf += '</div>';
    buf += '';
		return buf;

		buf = "<li><div class=\"panel panel-default\">";
		buf += "<div class=\"panel-body\">";
		buf += "<div class=\"panel-info\">";
		buf += "<p>Title: ";
		buf += this.title;
		buf += "</p> Version: ";
		buf += this.version + "<br />";
		buf += "Categories: " + this.categories + "<br />";
    buf += "</div>";
    buf += "</div>";
    buf += "</div>";
		return buf;
  }
}

var stats_no_items;
var stats_no_items_passed;
var stats_no_items_failed;
var stats_no_items_inapplicable;

function updateStats(data) {
	stats_no_items += 1;
	if (data.getResult() === "passed") {
		stats_no_items_passed += 1;
	} else if (data.getResult() === "failed") {
		stats_no_items_failed += 1;
	} else {
		stats_no_items_inapplicable += 1;
	}
}

function displayItemData() {
      var buf = "";
			stats_no_items = 0;
			stats_no_items_passed = 0;
			stats_no_items_failed = 0;
			stats_no_items_inapplicable = 0;

      $.each(item_data, function(i, item) {

				objectData = new ObjectData();
				objectData.read(item);
				updateStats(objectData);
				//console.log(objectData);
				buf += objectData.htmlize() + "<br />\n";
      });
      $("#fooooo").html(buf);

		  buf = "";
			buf += "Number of Items to display: " + item_data.length + "<br />";
			buf += "Number of Items passed: " + stats_no_items_passed + "<br />";
			buf += "Number of Items failed: " + stats_no_items_failed + "<br />";
			buf += "Number of Items inapplicable: " + stats_no_items_inapplicable + "<br />";
      $("#items-statistic").html(buf);
}

function displayDonut() {
  $("#doughnutChart").drawDoughnutChart([
    { title: "Passed",         value : stats_no_items_passed,  color: "#5BC394" },
    { title: "Failed",         value:  stats_no_items_failed,   color: "#D32F2F" },
    { title: "Inapplicable",   value : stats_no_items_inapplicable,    color: "#795548" }
  ]);
}

var obj = { "ordering": "by-submitting-date-reverse", "limit": 200 }

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
			displayDonut();
		}
	})
}

$(document).ready(function() {
    activaTab('tab1');
    loadItemData();
});
