



function activaTab(tab){
    $('.nav-tabs a[href="#' + tab + '"]').tab('show');
};


var item_data = null;

function humanRelativeDate(date) {
	var actual_date = new Date();
	var current_date_timezone_offset = actual_date.getTimezoneOffset();
	var offset = Math.abs(current_date_timezone_offset) * 60;
	var prev_date = new Date(date);
	var delta = Math.floor((actual_date - prev_date) / 1000) + offset;

	if (delta < 0)
	{
		return String(delta);
	}
	if (delta < 60)
	{
		return delta == 1 ? "one second ago" : delta + " seconds ago";
	}
	if (delta < 120)
	{
		return "a minute ago";
	}
	if (delta < 2700) // 45 * 60
	{
		return Math.ceil(delta / 60) + " minutes ago";
	}
	if (delta < 5400) // 90 * 60
	{
		return "an hour ago";
	}
	if (delta < 86400) // 24 * 60 * 60
	{
		return Math.ceil(delta / (60 * 60)) + " hours ago";
	}
	if (delta < 172800) // 48 * 60 * 60
	{
		return "yesterday";
	}
	if (delta < 2592000) // 30 * 24 * 60 * 60
	{
		return Math.ceil(delta / (60 * 60 * 24)) + " days ago";
	}
	if (delta < 31104000) // 12 * 30 * 24 * 60 * 60
	{
		return Math.ceil(delta / (60 * 60 * 24 * 30)) + " month ago (" +
			     prev_date.getUTCDate() + "-" +  (prev_date.getUTCMonth() + 1) + "-" +
					 prev_date.getUTCFullYear() + ")";
	}

	return prev_date.getUTCDate() + "-" +
		     (prev_date.getUTCMonth() + 1) + "-" +
				 prev_date.getUTCFullYear();
}


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
					references = data;
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

		var id_no = "-", date_added, test_date, result;

		if (item['object-achievements']) {
			$.each(item['object-achievements'], function(i, data) {
				if (i == 'id') {
					id_no = data;
				}
				if (i == 'date-added') {
					date_added = data;
				}
				if (i == 'test-date') {
					test_date = data;
				}
				if (i == 'test-result') {
					result = data;
				}
			});
		}

		this.id_no      = id_no;
		this.date_added = date_added;
		this.test_date  = test_date;
		this.result     = result;
	}


	this.getResult = function (item) {
		return this.result
	}

	this.htmlize = function () {
    var buf = '<div class="item-container">';
		if (this.result) {
			if (this.result == "passed") {
    		buf += '<div class="attachment-result result-bg-passed"></div>';
			} else if (this.result == "failed") {
    		buf += '<div class="attachment-result result-bg-failed"></div>';
			} else {
    		buf += '<div class="attachment-result result-bg-inapplicable"></div>';
			}
		} else {
    	buf += '<div class="attachment-result result-bg-inapplicable"></div>';
		}
    buf += '<div class="item-data">';
    buf += '<div class="item-container-title">';
    buf += this.title;
    buf += '</div>';
    buf += '<div class="item-data-left">';
    buf += '<div><strong>Last achievement:</strong> ';
    buf += '<span class="glyphicon glyphicon-time" aria-hidden="true"></span> ';
		if (this.test_date) {
			  buf += humanRelativeDate(this.test_date);
		} else {
    	buf += ' none ';
		}
    buf += '</div>';
    buf += '<div><strong>Submitter:</strong> ';
    buf += 'John Doe';
    buf += '</div>';

    buf += '<div><strong>No:</strong> ';
    buf += this.id_no;
    buf += '</div>';

    buf += '<div><strong>Result:</strong> ';
		if (this.result) {
			if (this.result == "passed") {
    		buf += '<span class="label label-success">passed</span>';
			} else if (this.result == "failed") {
    		buf += '<span class="label label-danger">failed</span>';
			} else {
    		buf += '<span class="label label-warning">not applicable</span>';
			}
		} else {
    	buf += '<span class="label label-warning">not applicable</span>';
		}
    buf += '</div>';
    buf += '</div>';
    buf += '<div class="item-data-middle"> ';
    buf += '<div><strong>Tags:</strong> ';
		if (this.tags) {
			for (var i in this.tags) {
				buf += '<span class="boxtag">' + this.tags[i] + '</span> ';
			}
		} else {
    	buf += 'no tags';
		}
    buf += '</div>';
    buf += '<div><strong>References:</strong> ';
		if (this.references) {
			for (var i in this.references) {
				splitted = this.references[i].split(":");
				buf += '<span class="refbox-left">' + splitted[0] + ':</span><span class="refbox-right">' + splitted[1] + '</span> ';
			}
		} else {
    	buf += 'no references';
		}
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

    buf += '<div><strong>Date added:</strong> ';
		if (this.date_added) {
			  buf += humanRelativeDate(this.date_added);
		} else {
    	buf += ' INTERNAL ERROR ';
		}
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
			buf += "Number of Items to Display: " + item_data.length + "<br />";
			buf += "<div class='ruler'></div>";
			buf += "Passed: " + stats_no_items_passed + "<br />";
			buf += "Failed: " + stats_no_items_failed + "<br />";
			buf += "Inapplicable: " + stats_no_items_inapplicable + "<br />";

			var all = stats_no_items_passed + stats_no_items_failed + stats_no_items_inapplicable;
			if (all > 0) {
				var stats_no_items_passed_pct = (stats_no_items_passed / all) * 100;
				var stats_no_items_failed_pct = (stats_no_items_failed / all) * 100;
				var stats_no_items_inapplicable_pct = (stats_no_items_inapplicable / all) * 100;
			} else {
				var stats_no_items_passed_pct = 0;
				var stats_no_items_failed_pct = 0;
				var stats_no_items_inapplicable_pct = 0;
		  }

			buf += '<div class="progress">';
			buf += '<div class="progress-bar progress-bar-success progress-bar-striped active" style="width: ' + stats_no_items_passed_pct  + '%">';
			buf += '<span class="sr-only">35% Complete (success)</span>';
			buf += '</div>';
			buf += '<div class="progress-bar progress-bar-danger progress-bar-striped active" style="width: ' + stats_no_items_failed_pct  + '%">';
			buf += '<span class="sr-only">10% Complete (danger)</span>';
			buf += '</div>';
			buf += '<div class="progress-bar progress-bar-warning progress-bar-striped active"" style="width: ' + stats_no_items_inapplicable_pct  + '%">';
			buf += '<span class="sr-only">20% Complete (warning)</span>';
			buf += '</div>';
			buf += '</div>';


      $("#items-statistic").html(buf);
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
		},
		success: function(data){
			item_data = data.data;
			displayItemData();
		}
	})
}

function readyBB() {
	$('.dropdown-menu li a').click(function(e){
		e.preventDefault();
		var selected = $(this).text();
		var cat = $(this).parents(".btn-group").find('button').attr("id");
		console.log(selected);
		console.log(cat);
		$(this).parents(".btn-group").find('.btn').html(selected + ' <span class="caret"></span>');

		urlParams[cat] = selected;
		reloadPageWithNewURL();
	});
}

function updateButtonSelection() {
	var buttons = $('.btn-group button');
	buttons.each(function( index ) {
		var v = $(this).attr("id");
		$(this).html(urlParams[v] + ' <span class="caret"></span>');
	});
}

$(document).ready(function() {
    activaTab(urlParams['tab']);
    loadItemData();
		readyBB();
		updateButtonSelection();
});


var urlParams = {
    limit: "Unlimited",
		filterByMaturityLevel: "All",
		filterByResult: "All",
		tab: "tab1",
};

(window.onpopstate = function () {
    var match,
        pl     = /\+/g,
        search = /([^&=]+)=?([^&]*)/g,
        decode = function (s) { return decodeURIComponent(s.replace(pl, " ")); },
        query  = window.location.search.substring(1);

    urlParams = urlParams;
    while (match = search.exec(query))
       urlParams[decode(match[1])] = decode(match[2]);
})();

console.log(urlParams);

function reloadPageWithNewURL()
{
	var parser = document.createElement('a');
	parser.href = document.URL;;

  var str = jQuery.param( urlParams );
  var url = parser.pathname + "?" + str;
  console.log(url);
	window.location.href = url;
}

//setTimeout(reloadPageWithNewURL, 1000);
