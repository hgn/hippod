function activaTab(tab){
    $('.nav-tabs a[href="#' + tab + '"]').tab('show');
};

$(document).ready(function() {

    activaTab('tab1');


});
