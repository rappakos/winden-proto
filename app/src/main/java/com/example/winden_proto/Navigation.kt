package com.example.winden_proto

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.winden_proto.Destinations.WELCOME_ROUTE
import com.example.winden_proto.Destinations.WINDE_ROUTE
import com.example.winden_proto.Destinations.FLUG_ROUTE
import com.example.winden_proto.welcome.WelcomeRoute

object Destinations {
        const val WELCOME_ROUTE = "welcome"
        const val WINDE_ROUTE = "winde"
        const val FLUG_ROUTE = "flug"
}

@Composable
fun WindenProtoNavHost(
        navController: NavHostController = rememberNavController(),
) {
  NavHost(
      navController = navController,
      startDestination = WELCOME_ROUTE,
  ) {
      composable(WELCOME_ROUTE) {
          WelcomeRoute(
              onSignInAsGuest = {
                  navController.navigate(WINDE_ROUTE)
              },
          )
      }
 }
}