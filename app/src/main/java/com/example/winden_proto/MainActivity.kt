package com.example.winden_proto

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.example.winden_proto.ui.theme.WindenProtoTheme
import com.example.winden_proto.WindenProtoNavHost

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            WindenProtoTheme {
                WindenProtoNavHost()
            }
        }
    }
}
