package dev.zantech.vocabtrainer.ui.sentence

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
fun SentenceScreen(
    viewModelFactory: ViewModelFactory,
    onSessionComplete: () -> Unit
) {
    val viewModel: SentenceViewModel = viewModel(factory = viewModelFactory)
    val state by viewModel.state.collectAsState()

    LaunchedEffect(state.sessionComplete) {
        if (state.sessionComplete) onSessionComplete()
    }

    val question = state.current
    Scaffold { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding).padding(24.dp)) {
            if (state.questions.isNotEmpty()) {
                LinearProgressIndicator(
                    progress = { state.index / state.questions.size.toFloat() },
                    modifier = Modifier.fillMaxWidth()
                )
                Text(
                    text = "${state.index + 1} / ${state.questions.size}",
                    modifier = Modifier.padding(top = 8.dp, bottom = 24.dp)
                )
            }

            if (question != null) {
                Text(text = "Complete the sentence", style = MaterialTheme.typography.labelLarge)
                Text(
                    text = question.blankedSentence,
                    style = MaterialTheme.typography.headlineSmall,
                    modifier = Modifier.padding(top = 8.dp, bottom = 8.dp)
                )
                Text(
                    text = "Hint: ${question.word.english}",
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(bottom = 32.dp)
                )

                question.choices.forEach { choice ->
                    SentenceChoiceButton(
                        choice = choice,
                        correctId = question.word.id,
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
private fun SentenceChoiceButton(
    choice: WordEntity,
    correctId: Int,
    selectedId: Int?,
    onClick: () -> Unit
) {
    val answered = selectedId != null
    val containerColor = when {
        !answered -> ButtonDefaults.buttonColors().containerColor
        choice.id == correctId -> Color(0xFF2E7D32)
        choice.id == selectedId -> Color(0xFFC62828)
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
        Text(choice.spanish)
    }
}
