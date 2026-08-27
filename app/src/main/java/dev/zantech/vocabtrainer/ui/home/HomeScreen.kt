package dev.zantech.vocabtrainer.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import dev.zantech.vocabtrainer.data.HomeState
import dev.zantech.vocabtrainer.ui.ViewModelFactory

@Composable
fun HomeScreen(
    viewModelFactory: ViewModelFactory,
    onPracticeFlashcards: () -> Unit,
    onTakeQuiz: () -> Unit,
    onConjugateVerbs: () -> Unit,
    onCompleteSentence: () -> Unit,
    onThematicLearning: () -> Unit
) {
    val viewModel: HomeViewModel = viewModel(factory = viewModelFactory)
    val state by viewModel.state.collectAsState()

    HomeScreenContent(
        state = state,
        onPracticeFlashcards = onPracticeFlashcards,
        onTakeQuiz = onTakeQuiz,
        onConjugateVerbs = onConjugateVerbs,
        onCompleteSentence = onCompleteSentence,
        onThematicLearning = onThematicLearning
    )
}

@Composable
private fun HomeScreenContent(
    state: HomeState,
    onPracticeFlashcards: () -> Unit,
    onTakeQuiz: () -> Unit,
    onConjugateVerbs: () -> Unit,
    onCompleteSentence: () -> Unit,
    onThematicLearning: () -> Unit
) {
    Scaffold { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "🔥 ${state.currentStreak} day streak",
                style = MaterialTheme.typography.headlineMedium
            )
            Text(
                text = "${state.masteredCount} / ${state.totalCount} words mastered",
                style = MaterialTheme.typography.bodyLarge,
                modifier = Modifier.padding(top = 8.dp, bottom = 32.dp)
            )
            Button(onClick = onPracticeFlashcards, modifier = Modifier.fillMaxWidth()) {
                Text("Practice Flashcards")
            }
            Button(
                onClick = onTakeQuiz,
                modifier = Modifier.fillMaxWidth().padding(top = 12.dp)
            ) {
                Text("Take Quiz")
            }
            Button(
                onClick = onConjugateVerbs,
                modifier = Modifier.fillMaxWidth().padding(top = 12.dp)
            ) {
                Text("Conjugate Verbs")
            }
            Button(
                onClick = onCompleteSentence,
                modifier = Modifier.fillMaxWidth().padding(top = 12.dp)
            ) {
                Text("Complete the Sentence")
            }
            OutlinedButton(
                onClick = onThematicLearning,
                modifier = Modifier.fillMaxWidth().padding(top = 20.dp)
            ) {
                Text("Thematic Learning")
            }
        }
    }
}
