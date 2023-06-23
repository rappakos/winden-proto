package com.example.winden_proto.welcome

import com.example.winden_proto.ui.theme.WindenProtoTheme

@Composable
fun WelcomeScreen(
    onSignInAsGuest: () -> Unit,
) {

            SignInCreateAccount(
                onSignInAsGuest = onSignInAsGuest,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 20.dp)
            )
        }
    }
}



@Preview(name = "Welcome light theme", uiMode = UI_MODE_NIGHT_YES)
@Preview(name = "Welcome dark theme", uiMode = UI_MODE_NIGHT_NO)
@Composable
fun WelcomeScreenPreview() {
    WindenProtoTheme {
        WelcomeScreen(
            onSignInAsGuest = {},
        )
    }
}