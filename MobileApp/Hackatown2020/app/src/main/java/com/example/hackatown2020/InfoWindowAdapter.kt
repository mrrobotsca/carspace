package com.example.hackatown2020

import android.app.Activity
import android.content.Context
import android.view.View
import com.google.android.gms.maps.GoogleMap
import com.google.android.gms.maps.model.Marker
import kotlinx.android.synthetic.main.custom_hoverbox.view.*

class CustomInfoWindowAdapter(val context: Context) : GoogleMap.InfoWindowAdapter{
    override fun getInfoWindow(p0: Marker?): View? {
        return  null
    }

    override fun getInfoContents(p0: Marker?): View {
        var mInfoView = (context as Activity).layoutInflater.inflate(R.layout.custom_hoverbox, null)
        var mInfoWindow: InfoWindowData? = p0?.tag as InfoWindowData?

        mInfoView.address.text = mInfoWindow?.address
        mInfoView.traffic.text = mInfoWindow?.traffic
        mInfoView.parking.text = mInfoWindow?.parking

        return mInfoView    }



}