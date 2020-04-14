package com.example.hackatown2020

import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationProvider
import android.os.Build
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.os.Looper
import android.widget.Toast
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.google.android.gms.location.*
import com.google.android.gms.maps.*
import com.google.android.gms.maps.GoogleMap.InfoWindowAdapter
import com.google.android.gms.maps.model.*

import java.net.CacheRequest

class MapsActivity : AppCompatActivity(), OnMapReadyCallback {

    private lateinit var mMap: GoogleMap

    private var latitude: Double = 0.toDouble()
    private var longitude: Double = 0.toDouble()
    private val customInfoWindowAdapter = CustomInfoWindowAdapter(this)


    private lateinit var mLastLocation: Location
    private var mMarker: Marker?=null

    //Location
    lateinit var fusedLocationProviderClient: FusedLocationProviderClient
    lateinit var locationRequest: LocationRequest
    lateinit var locationCallback: LocationCallback

    companion object{
        private const val MY_PERMISSION_CODE: Int = 1000
    }

    val latLngIkea1: LatLng = LatLng(45.496134, -73.691364)
    val infoIkea1: InfoWindowData= InfoWindowData("9191 Cavendish Blvd, Montreal, Quebec H4T 1M8", "Élevé", " 2 places disponibles")
    val latLngIkea2: LatLng = LatLng(45.575692, -73.404109)
    val infoIkea2: InfoWindowData= InfoWindowData("586 Chemin de Touraine, Boucherville, QC J4B 5E4", "Faible", " 55 places disponibles")
    val latLngCostco1: LatLng = LatLng(45.492680, -73.554828)
    val infoCostco1: InfoWindowData= InfoWindowData("300 Rue Bridge, Montréal, QC H3K 2C3", "Élevé", " 4 places disponibles")
    val latLngCostco2: LatLng = LatLng(45.536603, -73.660071)
    val infoCostco2: InfoWindowData= InfoWindowData("1015 Rue Du Marché Central, Montreal, Quebec H4N 3J8", "Moyen", " 36 places disponibles")
    val latLngCostco3: LatLng = LatLng(45.575277, -73.755863)
    val infoCostco3: InfoWindowData= InfoWindowData("2999, Autoroute 440, Laval, QC H7P 4W5", "Moyen", " 20 places disponibles")
    val latLngCostco4: LatLng = LatLng(45.469426, -73.817888)
    val infoCostco4: InfoWindowData= InfoWindowData("5701 Trans-Canada Hwy, Pointe-Claire, Quebec H9R 5E8", "Moyen", " 24 places disponibles")

    var infoAndLocalityArray = arrayListOf<InfoAndLocality>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_maps)
        // Obtain the SupportMapFragment and get notified when the map is ready to be used.
        val mapFragment = supportFragmentManager
            .findFragmentById(R.id.map) as SupportMapFragment
        mapFragment.getMapAsync(this)

        //Request run time location
        if(checkLocationPermission()){
            buildLocationRequest()
            buildLocationCallBack()
            fusedLocationProviderClient = LocationServices.getFusedLocationProviderClient(this)
            fusedLocationProviderClient.requestLocationUpdates(locationRequest,locationCallback, Looper.myLooper())
        }

        infoAndLocalityArray = arrayListOf<InfoAndLocality>(
            InfoAndLocality(latLngIkea1,infoIkea1),
            InfoAndLocality(latLngIkea2,infoIkea2),
            InfoAndLocality(latLngCostco2,infoCostco2),
            InfoAndLocality(latLngCostco1,infoCostco1),
            InfoAndLocality(latLngCostco3,infoCostco3),
            InfoAndLocality(latLngCostco4,infoCostco4))


    }

    private fun buildLocationCallBack() {
        locationCallback = object : LocationCallback() {
            override fun onLocationResult(p0: LocationResult?) {
                mLastLocation = p0!!.locations[p0.locations.size - 1]
                if (mMarker != null) {
                    mMarker!!.remove()
                }
                latitude = mLastLocation.latitude
                longitude = mLastLocation.longitude

                val info: InfoWindowData= InfoWindowData("hellodadawbndkmlawd", "fghjkl", " gubyhinjuomk")

                mMap.setInfoWindowAdapter(customInfoWindowAdapter)

                val latLng = LatLng(latitude, longitude)
                val markerOptions = MarkerOptions()
                    .position(latLng)
                    //.title("Your position")
                    .icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_GREEN))

                mMarker = mMap.addMarker(markerOptions)
                mMarker!!.tag = info

                // Move Camera
                mMap!!.animateCamera(CameraUpdateFactory.newLatLngZoom(latLng,12f))


            }
        }
    }

    private fun buildLocationRequest() {
        locationRequest = LocationRequest()
        locationRequest.priority = LocationRequest.PRIORITY_HIGH_ACCURACY
        locationRequest.interval = 5000
        locationRequest.fastestInterval = 3000
        locationRequest.smallestDisplacement = 10f
    }

    private fun checkLocationPermission(): Boolean {

        if(ContextCompat.checkSelfPermission(this,android.Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED){
            if(ActivityCompat.shouldShowRequestPermissionRationale(this,android.Manifest.permission.ACCESS_FINE_LOCATION)){
                ActivityCompat.requestPermissions(this, arrayOf(android.Manifest.permission.ACCESS_FINE_LOCATION), MY_PERMISSION_CODE)
            }else{
                ActivityCompat.requestPermissions(this, arrayOf(android.Manifest.permission.ACCESS_COARSE_LOCATION), MY_PERMISSION_CODE)
            }
            return false
        }
        else
            return true
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        when(requestCode){
            MY_PERMISSION_CODE->{
                if(grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED){
                    if(ContextCompat.checkSelfPermission(this, android.Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED)
                        if (checkLocationPermission()){
                            buildLocationRequest()
                            buildLocationCallBack()
                            fusedLocationProviderClient = LocationServices.getFusedLocationProviderClient(this)
                            fusedLocationProviderClient.requestLocationUpdates(locationRequest,locationCallback, Looper.myLooper())
                            mMap.isMyLocationEnabled = true
                        }
                }else{
                    Toast.makeText(this, "Permission Denied",Toast.LENGTH_SHORT).show()
                }
            }

        }
    }

    override fun onStop() {
        fusedLocationProviderClient.removeLocationUpdates(locationCallback)
        super.onStop()
    }

    var markerArray: ArrayList<Marker> = ArrayList(infoAndLocalityArray.size)


    override fun onMapReady(googleMap: GoogleMap) {
        mMap = googleMap

        mMap.setInfoWindowAdapter(customInfoWindowAdapter)

        for( (index, value) in infoAndLocalityArray.withIndex()){
            markerArray!!.add(mMap.addMarker(MarkerOptions()
                .position(value.latLng)
                .icon(BitmapDescriptorFactory.defaultMarker(BitmapDescriptorFactory.HUE_RED))
            ))
            markerArray[index]!!.tag = value.infoWindowData
        }


        if(ContextCompat.checkSelfPermission(this,android.Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED){
            mMap.isMyLocationEnabled = true
        }
        mMap.uiSettings.isZoomControlsEnabled = true
    }
}

