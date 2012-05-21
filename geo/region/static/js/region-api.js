var user = requestUserRegion();
$(document).ready(function() {
    if (user.source != 'session' && navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            requestUserRegion(position, true);
        });
    }
});
function coordToPosition(data) {
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({'latLng': data}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            var city = geocoderToCity(results[0]);
            if (city != user.place.city && city != '') {
                $("#other-region a").html(city);
                $("#other-region").show();
            }
            else {
                $("#other-region").hide();
            }
        } else {
            alert("Geocode was not successful for the following reason: " + status);
        }
    });
}

function addressToPosition(data) {
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({'address': data}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            userPosition = results[0].geometry.location;
            $("#user-map").map_plugin('setUserMarker', userPosition);
        } else {
            $('.error-null').show();
        }
    });
}

function getUserRegionObject() {
    if (navigator.geolocation) {
        var coords = {};
        var watchId = navigator.geolocation.watchPosition(function(position) {
            coords = position.coords;
        });
        console.log(watchId);
        console.log(coords);
    }
}

function requestUserRegion(position, reload) {
    var request = {};
    if (position != undefined) {
        console.log(position);
        request = {
            filter: [
                {
                    property: 'coord',
                    value: {
                        lat: position.coords.latitude,
                        lon: position.coords.longitude
                    }
                }
            ]
        }
        request.filter = JSON.stringify(request.filter);
    }
    var user;
    $.ajax({
        url: '/user-region/',
        dataType: 'json',
        data: request,
        async: false,
        success: function(response) {
            user = response;
            if (reload === true) {
                var request = {
                    filter: [
                        {
                            property: 'coord',
                            value: user.coord
                        },
                        {
                            property: 'place',
                            value: user.place
                        }
                    ]
                };
                request.filter = JSON.stringify(request.filter);
                $.ajax({
                    url: '/user-region/set',
                    dataType: 'json',
                    data: request,
                    async: false
                });
                window.location.reload();
            }
        }
    });
    
    return user;
}
