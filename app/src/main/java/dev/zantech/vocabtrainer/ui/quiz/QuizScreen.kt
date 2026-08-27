package dev.zantech.vocabtrainer.ui.quiz

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import dev.zantech.vocabtrainer.data.WordEntity
import dev.zantech.vocabtrainer.ui.ViewModelFactory

@Composable
fun QuizScreen(
    viewModelFactory: ViewModelFactory,
    onSessionComplete: () -> Unit
) {
    val viewModel: QuizViewModel = viewModel(factory = viewModelFactory)
    val state by viewModel.state.collectAsState()

    LaunchedEffect(state.sessionComplete) {
        if (state.sessionComplete) onSessionComplete()
    }

    val word = state.currentWord
    Scaffold { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding).padding(24.dp)) {
            if (state.words.isNotEmpty()) {
                LinearProgressIndicator(
                    progress = { state.index / state.words.size.toFloat() },
                    modifier = Modifier.fillMaxWidth()
                )
                Text(
                    text = "${state.index + 1} / ${state.words.size}",
                    modifier = Modifier.padding(top = 8.dp, bottom = 24.dp)
                )
            }

            if (word != null) {
                Text(text = word.partOfSpeech, style = MaterialTheme.typography.labelLarge)
                Text(
                    text = word.spanish,
                    style = MaterialTheme.typography.displaySmall,
                    modifier = Modifier.padding(top = 8.dp, bottom = 32.dp)
                )

                state.choices.forEach { choice ->
                    ChoiceButton(
                        choice = choice,
                        correctId = word.id,
                        selectedId = state.selectedId,
                        onClick = { viewModel.selectAnswer(choice) }
                    )
                }

                if (state.answered) {
                    Button(
                        onClick = { viewModel.next() },
                        modifier = Modifier.fillMaxWidth().padding(top = 16.dp)
                    ) {
                        Text("Next")
                    }
                }
            }
        }
    }
}

@Composable
private fun ChoiceButton(
    choice: WordEntity,
    correctId: Int,
    selectedId: Int?,
    onClick: () -> Unit
) {
    val answered = selectedId != null
    val isCorrectChoice = choice.id == correctId
    val isSelected = choice.id == selectedId

    // Immediate feedback per CLAUDE.md §4: green for the correct answer once answered,
    // red for a wrong pick, default otherwise.
    val containerColor = when {
        !answered -> ButtonDefaults.buttonColors().containerColor
        isCorrectChoice -> Color(0xFF2E7D32)
        isSelected -> Color(0xFFC62828)
        else -> ButtonDefaults.buttonColors().containerColor
    }

    Button(
        onClick = onClick,
        enabled = !answered,
        colors = ButtonDefaults.buttonColors(
            containerColor = containerColor,
            disabledContainerColor = containerColor
        ),
        modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp)
    ) {
        Text(choice.english)
    }
}
