package dev.zantech.vocabtrainer.ui.thematic

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import androidx.compose.runtime.mutableStateMapOf
import dev.zantech.vocabtrainer.data.WordEntity
import dev.zantech.vocabtrainer.ui.ViewModelFactory
import kotlinx.coroutines.launch
import androidx.compose.runtime.rememberCoroutineScope

@Composable
fun ThematicCategoryScreen(
    category: String,
    viewModelFactory: ViewModelFactory,
    onBack: () -> Unit
) {
    val repository = viewModelFactory.repository
    val scope = rememberCoroutineScope()
    var words by remember(category) { mutableStateOf<List<WordEntity>>(emptyList()) }
    val revealed = remember(category) { mutableStateMapOf<Int, Boolean>() }

    LaunchedEffect(category) {
        words = repository.unlockedWordsIn(category)
    }

    Scaffold { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding).padding(24.dp)) {
            Text(
                text = category.replaceFirstChar { it.uppercase() },
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier.padding(bottom = 4.dp)
            )
            Text(
                text = "${words.size} word${if (words.size == 1) "" else "s"} unlocked so far. Tap a card to reveal.",
                style = MaterialTheme.typography.bodyMedium,
                modifier = Modifier.padding(bottom = 16.dp)
            )
            LazyColumn {
                items(words, key = { it.id }) { word ->
                    val isRevealed = revealed[word.id] == true
                    WordCard(
                        word = word,
                        revealed = isRevealed,
                        onReveal = { revealed[word.id] = true },
                        onAnswer = { gotIt ->
                            scope.launch {
                                repository.recordFlashcardResult(word, gotIt)
                                // Collapse the card and re-pull from DB so the mastered
                                // star reflects the just-recorded answer — visible proof
                                // the tap did something.
                                revealed[word.id] = false
                                words = repository.unlockedWordsIn(category)
                            }
                        }
                    )
                }
            }
            Button(onClick = onBack, modifier = Modifier.fillMaxWidth().padding(top = 8.dp)) {
                Text("Back to categories")
            }
        }
    }
}

@Composable
private fun WordCard(
    word: WordEntity,
    revealed: Boolean,
    onReveal: () -> Unit,
    onAnswer: (Boolean) -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 6.dp)
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .clickable(enabled = !revealed, onClick = onReveal)
            .padding(16.dp)
    ) {
        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(text = word.spanish, style = MaterialTheme.typography.titleLarge)
            if (word.mastered) {
                Text(text = "★ mastered", style = MaterialTheme.typography.labelMedium)
            }
        }
        if (revealed) {
            Text(
                text = word.english,
                style = MaterialTheme.typography.bodyLarge,
                modifier = Modifier.padding(top = 8.dp)
            )
            Text(
                text = word.example,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 4.dp)
            )
            Row(modifier = Modifier.fillMaxWidth().padding(top = 12.dp)) {
                Button(onClick = { onAnswer(false) }, modifier = Modifier.weight(1f)) {
                    Text("Still learning")
                }
                Button(
                    onClick = { onAnswer(true) },
                    modifier = Modifier.weight(1f).padding(start = 8.dp)
                ) {
                    Text("Got it")
                }
            }
        } else {
            Text(
                text = "Tap to reveal",
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(top = 8.dp)
            )
        }
    }
}
