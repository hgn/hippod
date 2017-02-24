"use strict";

hippoD.controller("DashboardCtrl", function ($scope, ResourcesService, ResultService) {


  $scope.diskConsumptionData = null;

	ResourcesService.getRessource().then(function(res) {
		var data_array = res['data']['data']['item-bytes-overtime']
		var bytes_actual = data_array[data_array.length - 1][1]
		$scope.overall_data_byte_human = prettyNumber(bytes_actual, 'iec');
		$scope.overall_data_byte_vanilla = bytes_actual;

		var new_array = new Array();
		var new_array2 = new Array();
		var new_array3 = new Array();
		angular.forEach(data_array, function(value, key) {
			var unix_tm = new Date(value[0]).getTime() / 1000;
			new_array.push([unix_tm, value[1]]);
			new_array2.push([unix_tm, value[2]]);
			new_array3.push([unix_tm, value[3]]);
		});

    $scope.diskConsumptionData = [
			{
				"key": "Series 1",
				"values": new_array
			},
			{
				"key": "Series 2",
				"values": new_array2
			},
			{
				"key": "Series 3",
				"values": new_array3
			}
    ];

	}, function(error) {
		$scope.overall_data_byte_human = "unknown (API error)";
		$scope.overall_data_byte_vanilla = "unknown (API error)";
	});


    $scope.options = {
        chart: {
            type: 'stackedAreaChart',
            height: 355,
            margin : {
                top: 145,
                right: 0,
                bottom: 40,
                left: 75
            },
            x: function(d){return d[0];},
            y: function(d){return d[1];},
            useVoronoi: false,
            clipEdge: true,
            duration: 100,
            useInteractiveGuideline: true,
            xAxis: {
                showMaxMin: false,
                axisLabel: 'Date',
                tickFormat: function(d) {
                    return d3.time.format("%x")(new Date(d * 1000));
                }
            },
            yAxis: {
                axisLabel: 'Amount of Tests',
                tickFormat: function(d){
                    return d3.format()(d);
                }
            },
            zoom: {
                enabled: true,
                scaleExtent: [1, 10],
                useFixedDomain: false,
                useNiceScale: false,
                horizontalOff: false,
                verticalOff: true,
                unzoomEventType: 'dblclick.zoom'
            }
        }
    };

    ResultService.getResults().then(function(res) {
        $scope.data_sunburn = res['achievement-results-sunburn-chart'];
        $scope.achievements_over_time = [
            {"key": "passed",
             "values": res['achievements-by-time']['passed']},
            {"key": "failed",
             "values": res['achievements-by-time']['failed']},
            {"key": "nonapplicable",
             "values": res['achievements-by-time']['nonapplicable']}
        ]
        createVisualization($scope.data_sunburn)
        });


	$scope.yAxisTickFormatFunction = function(){
		return function(d){
      return prettyNumber(d, 'iec');
		}
	}


// <------ Configuration and execution of sunburn chart from here ------>

// Dimensions of sunburst.
var width = 300;
var height = 300;
var radius = Math.min(width, height) / 2;

// Breadcrumb dimensions: width, height, spacing, width of tip/tail.
var b = {
  w: 130, h: 30, s: 3, t: 10
};

var colors_global = {};

// look for the nearest color hash in the color matrix to get
// desired and not random color
function binarySearch(color_matrix, hash, root_hash) {
    var index_matrix = root_hash % color_matrix.length;
    var color_list = color_matrix[index_matrix];
    if (hash == root_hash) {
        return color_list[0]
    }
    var index = hash % color_list.length
    var color = color_list[index]
    return color
}

// assign color to name for the legend
function set_color(name, color) {
    if (name == 'init') {
        return
    }
    if (!(name in colors_global)) {
        colors_global[name] = color
    }
}

// get hash for the rgb color by name
function hashCode(name, cat_root) {
  var hash = 0;
  for (var i = 0; i < name.length; i++) {
    var char = name.charCodeAt(i)
    var hash1 = char + ((char << 8) - hash);
    var hash2 = char + ((char << 12) - hash);
    var hash3 = char + ((char << 16) - hash);
    hash = (hash1 ^ hash2 ^ hash3)
  }
  hash  = (hash & 0x0000FFFFFF)
  var root_hash = 0;
  for (var i = 0; i < cat_root.length; i++) {
    var char = cat_root.charCodeAt(i)
    var hash1 = char + ((char << 8) - root_hash);
    var hash2 = char + ((char << 12) - root_hash);
    var hash3 = char + ((char << 16) - root_hash);
    root_hash = (hash1 ^ hash2 ^ hash3)
  }
  root_hash  = (root_hash & 0x0000FFFFFF)
  return [hash, root_hash]
};

// 2D Array helps to set color in consistent order
// the very first element in the categories hierarchy defines the list
function inToRGB(hash_list) {
  var hash_name = hash_list[0]
  var root_hash = hash_list[1]
  var colors = [[0x37474f, 0x455a64, 0x546e7a, 0x607d8b],       // Blue Grey
                [0x424242, 0x616161, 0x757575, 0x9e9e9e],       // Grey
                [0x4e342e, 0x5d4037, 0x6d4c41, 0x795548],       // Brown
                [0xd84315, 0xe64a19, 0xf4511e, 0xff5722],       // Deep Orange
                [0xef6c00, 0xf57c00, 0xfb8c00, 0xff9800],       // Orange
                [0xff8f00, 0xffa000, 0xffb300, 0xffc107],       // Amber
                [0xf9a825, 0xfbc02d, 0xfdd835, 0xffeb3b],       // Yellow
                [0x9e9d24, 0xafb42b, 0xc0ca33, 0xcddc39],       // Lime
                [0x558b2f, 0x689f38, 0x7cb342, 0x8bc34a],       // Light Green
                [0x2e7d32, 0x388e3c, 0x43a047, 0x4caf50],       // Green
                [0x00695c, 0x00796b, 0x00897b, 0x009688],       // Teal
                [0x00838f, 0x0097a7, 0x00acc1, 0x00bcd4],       // Cyan
                [0x0277bd, 0x0288d1, 0x039be5, 0x03a9f4],       // Light Blue
                [0x1565c0, 0x1976d2, 0x1e88e5, 0x2196f3],       // Blue
                [0x283593, 0x303f9f, 0x3949ab, 0x3f51b5],       // Indigo
                [0x4527a0, 0x512da8, 0x5e35b1, 0x673ab7],       // Deep Purple
                [0x6a1b9a, 0x7b1fa2, 0x8e24aa, 0x9c27b0],       // Purple
                [0xad1457, 0xc2185b, 0xd81b60, 0xe91e63],       // Pink
                [0xc62828, 0xd32f2f, 0xe53935, 0xf44336]];
  var c = (hash_name & 0x00FFFFFF)
        .toString(16)
        .toUpperCase();
  var hex = hash_name.toString(16);
  var result = binarySearch(colors, hash_name, root_hash);
  hex = (result & 0x00FFFFFF)
  hex = hex.toString(16);
  hex = hex.toUpperCase();
  return "#" + "00000".substring(0, 6 - hex.length) + hex
};

// Mapping of step names to colors.
function get_color(name, cat_root) {
  var color = inToRGB(hashCode(name, cat_root))
  set_color(name, color)
  return color
}

// Total size of all segments; we set this later, after loading the data.
var totalSize = 0;

var vis = d3.select("#drawSunBurst").append("svg:svg")
    .attr("width", width)
    .attr("height", height)
    .append("svg:g")
    .attr("id", "container")
    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");

var partition = d3.layout.partition()
    .sort(null)
    .size([2 * Math.PI, radius * radius])
    .value(function(d) {return d.size; });


var arc = d3.svg.arc()
    .startAngle(function(d) { return d.x; })
    .endAngle(function(d) { return d.x + d.dx; })
    .innerRadius(function(d) { return Math.sqrt(d.y); })
    .outerRadius(function(d) { return Math.sqrt(d.y + d.dy); });


// Main function to draw and set up the visualization, once we have the data.
function createVisualization(json) {
  // Basic setup of page elements.
  initializeBreadcrumbTrail();
  d3.select("#togglelegend").on("click", toggleLegend);

  // Bounding circle underneath the sunburst, to make it easier to detect
  // when the mouse leaves the parent g.
  vis.append("svg:circle")
      .attr("r", radius)
      .style("opacity", 0);

  // For efficiency, filter nodes to keep only those large enough to see.
  var nodes = partition.nodes(json)
      .filter(function(d) {
      return (d.dx > 0.005); // 0.005 radians = 0.29 degrees
      });

  var path = vis.data([json]).selectAll("path")
      .data(nodes)
      .enter().append("svg:path")
      .attr("display", function(d) { return d.depth ? null : "none"; })
      .attr("d", arc)
      .attr("fill-rule", "evenodd")
      .style("fill", function(d) { return get_color(d.name, d.root); })
      .style("opacity", 1)
      .on("mouseover", mouseover);

  // Add the mouseleave handler to the bounding circle.
  d3.select("#container").on("mouseleave", mouseleave);

  // Get total size of the tree = value of root node from partition.
  totalSize = path.node().__data__.value;
  drawLegend();
 };

// Fade all but the current sequence, and show it in the breadcrumb trail.
function mouseover(d) {
  var percentage = (100 * d.value / totalSize).toPrecision(3);
  var percentageString = percentage + "%";
  if (percentage < 0.1) {
    percentageString = "< 0.1%";
  }
  d3.select("#statistics-percentage")
      .text(percentageString);

  d3.select("#statistics-explanation")
      .style("visibility", "");

  var sequenceArray = getAncestors(d);
  updateBreadcrumbs(sequenceArray, percentageString);

  // Fade all the segments.
  d3.selectAll("path")
      .style("opacity", 0.3);

  // Then highlight only those that are an ancestor of the current segment.
  vis.selectAll("path")
      .filter(function(node) {
                return (sequenceArray.indexOf(node) >= 0);
              })
      .style("opacity", 1);
}

// Restore everything to full opacity when moving off the visualization.
function mouseleave(d) {

  // Hide the breadcrumb trail
  d3.select("#trail")
      .style("visibility", "hidden");

  // Deactivate all segments during transition.
  d3.selectAll("path").on("mouseover", null);

  // Transition each segment to full opacity and then reactivate it.
  d3.selectAll("path")
      .transition()
      .duration(1000)
      .style("opacity", 1)
      .each("end", function() {
              d3.select(this).on("mouseover", mouseover);
            });

  d3.select("#statistics-explanation")
      .style("visibility", "hidden");
}

// Given a node in a partition layout, return an array of all of its ancestor
// nodes, highest first, but excluding the root.
function getAncestors(node) {
  var path = [];
  var current = node;
  while (current.parent) {
    path.unshift(current);
    current = current.parent;
  }
  return path;
}

function initializeBreadcrumbTrail() {
  // Add the svg area.
  var trail = d3.select("#statistics-sequence").append("svg:svg")
      .attr("width", width)
      .attr("height", 50)
      .attr("id", "trail");
  // Add the label at the end, for the percentage.
  trail.append("svg:text")
    .attr("id", "endlabel")
    .style("fill", "#000");
}

// Generate a string that describes the points of a fbreadcrumb polygon.
function breadcrumbPoints(d, i) {
  var points = [];
  points.push("0,0");
  points.push(b.w + ",0");
  points.push(b.w + b.t + "," + (b.h / 2));
  points.push(b.w + "," + b.h);
  points.push("0," + b.h);
  if (i > 0) { // Leftmost breadcrumb; don't include 6th vertex.
    points.push(b.t + "," + (b.h / 2));
  }
  return points.join(" ");
}

// Update the breadcrumb trail to show the current sequence and percentage.
function updateBreadcrumbs(nodeArray, percentageString) {

  // Data join; key function combines name and depth (= position in sequence).
  var g = d3.select("#trail")
      .selectAll("g")
      .data(nodeArray, function(d) { return d.name + d.depth; });

  // Add breadcrumb and label for entering nodes.
  var entering = g.enter().append("svg:g");

  entering.append("svg:polygon")
      .attr("points", breadcrumbPoints)
      .style("fill", function(d) { return get_color(d.name, d.root); });

  entering.append("svg:text")
      .attr("x", (b.w + b.t) / 2)
      .attr("y", b.h / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", "middle")
      .text(function(d) { return d.name; });

  // Set position for entering and updating nodes.
  g.attr("transform", function(d, i) {
    return "translate(" + i * (b.w + b.s) + ", 0)";
  });

  // Remove exiting nodes.
  g.exit().remove();

  // Now move and update the percentage at the end.
  d3.select("#trail").select("#endlabel")
      .attr("x", (nodeArray.length + 0.5) * (b.w + b.s))
      .attr("y", b.h / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", "middle")
      .text(percentageString);

  // Make the breadcrumb trail visible, if it's hidden.
  d3.select("#trail")
      .style("visibility", "");

}

function drawLegend() {
  // Dimensions of legend item: width, height, spacing, radius of rounded rect.
  var li = {
    w: 160, h: 20, s: 3, r: 3
  };

  var legend = d3.select("#statistics-legend").append("svg:svg")
      .attr("width", li.w)
      .attr("height", d3.keys(colors_global).length * (li.h + li.s));

  var g = legend.selectAll("g")
      .data(d3.entries(colors_global))
      .enter().append("svg:g")
      .attr("transform", function(d, i) {
              return "translate(0," + i * (li.h + li.s) + ")";
           });

  g.append("svg:rect")
      .attr("rx", li.r)
      .attr("ry", li.r)
      .attr("width", li.w)
      .attr("height", li.h)
      .style("fill", function(d) { return d.value; });

  g.append("svg:text")
      .attr("x", li.w / 2)
      .attr("y", li.h / 2)
      .attr("dy", "0.35em")
      .attr("text-anchor", "middle")
      .text(function(d) { return d.key; });
}

function toggleLegend() {
  var legend = d3.select("#statistics-legend");
  if (legend.style("visibility") == "hidden") {
    legend.style("visibility", "");
  } else {
    legend.style("visibility", "hidden");
  }
}

});