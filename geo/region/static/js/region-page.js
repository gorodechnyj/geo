$(document).ready(function() {
    $("#user_region").autocomplete({
        source: function(request, response) {
            $.getJSON('/user-region/autocomplete', {'startsWith': request.term}, function(data) {
                if (data.status == 'OK') response(data.regions);
            });
        },
        minLength: 2  
    });
    
    $("#user-map").map_plugin({'userDraggable': true});
    $("#user-map").map_plugin('addListener', 'mapClicked', function(event) {$("#user-map").map_plugin('setUserMarker', event.latLng); coordToPosition(event.latLng);});
    $("#user-map").map_plugin('addListener', 'userPositionChanged', function(event) {coordToPosition(event.latLng);});
    
    $("#other-region").hide();
    $("#other-region a").click(function() {
        $("#user_region").val($(this).html());
        $("#user_region").autocomplete("search");
        $("#user_region").focus();
        return false;
    });
    
    // Поиск введенного города на карте
    $("#regionFind").click(function() {
        addressToPosition($("#user_region").val());
    });
    
    $("#user_region_submit").click(function() {
        $.getJSON('user-region/validate', {'user_region': $("#user_region").val()}, function(data){
            switch(data.status) {
                case 'OK':
                    var sub = {};
                    var pos = $("#user-map").map_plugin('getProp', 'userMarker');
                    $("#user_region_form input[name=city]").val(data.place.city);
                    $("#user_region_form input[name=region]").val(data.place.region);
                    $("#user_region_form input[name=lat]").val(pos.position.lat());
                    $("#user_region_form input[name=lon]").val(pos.position.lng());
                    $("#user_region_form").submit();
                    break;
                case 'AMBIGOUS':
                    $(".error-ambigous").show();
                    break;
                default:
                    $(".error-null").show();
                    break;
            }
        });
        return false;
    });
});