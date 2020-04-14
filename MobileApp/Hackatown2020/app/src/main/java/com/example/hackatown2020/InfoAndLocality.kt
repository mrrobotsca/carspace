package com.example.hackatown2020

import com.google.android.gms.maps.model.LatLng

data class InfoAndLocality(
    var latLng: LatLng,
    var infoWindowData: InfoWindowData
)