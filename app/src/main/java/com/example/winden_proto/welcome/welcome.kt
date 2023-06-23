package com.example.winden_proto.welcome



import androidx.compose.runtime.Composable
import androidx.lifecycle.viewmodel.compose.viewModel

@Composable
fun WelcomeRoute(
    onSignInAsGuest: () -> Unit,
) {
    val welcomeViewModel: WelcomeViewModel = viewModel(factory = WelcomeViewModelFactory())

    WelcomeScreen(
        onSignInAsGuest = {
            welcomeViewModel.signInAsGuest(onSignInAsGuest)
        },
    )
}