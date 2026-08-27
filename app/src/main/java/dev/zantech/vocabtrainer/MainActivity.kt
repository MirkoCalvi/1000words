package dev.zantech.vocabtrainer

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import dev.zantech.vocabtrainer.ui.ViewModelFactory
import dev.zantech.vocabtrainer.ui.nav.VocabNavHost
import dev.zantech.vocabtrainer.ui.theme.VocabTrainerTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val app = application as VocabTrainerApp
        val viewModelFactory = ViewModelFactory(app.container.repository)

        setContent {
            VocabTrainerTheme {
                Surface(modifier = Modifier.fillMaxSize()) {
                    VocabNavHost(viewModelFactory = viewModelFactory)
                }
            }
        }
    }
}
