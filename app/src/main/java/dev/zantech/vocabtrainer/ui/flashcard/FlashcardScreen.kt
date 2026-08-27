package dev.zantech.vocabtrainer.ui.flashcard

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import dev.zantech.vocabtrainer.ui.ViewModelFactory

@Composable
fun FlashcardScreen(
    viewModelFactory: ViewModelFactory,
    onSessionComplete: () -> Unit
) {
    val viewModel: FlashcardViewModel = viewModel(factory = viewModelFactory)
    val state by viewModel.state.collectAsState()

    LaunchedEffect(state.sessionComplete) {
        if (state.sessionComplete) onSessionComplete()
    }

    val word = state.currentWord
    Scaffold { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding).padding(24.dp)) {
            if (state.words.isNotEmpty()) {
                LinearProgressIndicator(
                    progress = { (state.index) / state.words.size.toFloat() },
                    modifier = Modifier.fillMaxWidth()
                )
                Text(
                    text = "${state.index + 1} / ${state.words.size}",
                    modifier = Modifier.padding(top = 8.dp, bottom = 24.dp)
                )
            }

            if (word != null) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f)
                        .clickable(enabled = !state.revealed) { viewModel.reveal() },
                ) {
                    Column(
                        modifier = Modifier.fillMaxSize().padding(24.dp),
                        verticalArrangement = Arrangement.Center,
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(text = word.partOfSpeech, style = MaterialTheme.typography.labelLarge)
                        Text(
                            text = word.spanish,
                            style = MaterialTheme.typography.displaySmall,
                            modifier = Modifier.padding(top = 8.dp)
                        )
                        if (state.revealed) {
                            Text(
                                text = word.english,
                                style = MaterialTheme.typography.headlineSmall,
                                modifier = Modifier.padding(top = 24.dp)
                            )
                            Text(
                                text = word.example,
                                style = MaterialTheme.typography.bodyMedium,
                                modifier = Modifier.padding(top = 12.dp)
                            )
                        } else {
                            Text(
                                text = "Tap to reveal",
                                style = MaterialTheme.typography.bodyMedium,
                                modifier = Modifier.padding(top = 24.dp)
                            )
                        }
                    }
                }

                if (state.revealed) {
                    Row(modifier = Modifier.fillMaxWidth().padding(top = 16.dp)) {
                        Button(
                            onClick = { viewModel.answer(false) },
                            modifier = Modifier.weight(1f)
                        ) {
                            Text("Still learning")
                        }
                        Button(
                            onClick = { viewModel.answer(true) },
                            modifier = Modifier.weight(1f).padding(start = 12.dp)
                        ) {
                            Text("Got it")
                        }
                    }
                } else {
                    // Reserve the same height as the answer row so the card doesn't jump.
                    Row(modifier = Modifier.fillMaxWidth().height(48.dp).padding(top = 16.dp)) {}
                }
            }
        }
    }
}
