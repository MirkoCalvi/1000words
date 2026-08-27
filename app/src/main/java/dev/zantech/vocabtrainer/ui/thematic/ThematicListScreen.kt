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
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import dev.zantech.vocabtrainer.data.CategorySummary
import dev.zantech.vocabtrainer.ui.ViewModelFactory

/** One capitalized display label per category slug, falls back to the slug itself. */
private fun displayName(category: String): String =
    category.replaceFirstChar { it.uppercase() }

@Composable
fun ThematicListScreen(
    viewModelFactory: ViewModelFactory,
    onOpenCategory: (String) -> Unit
) {
    val viewModel: ThematicListViewModel = viewModel(factory = viewModelFactory)
    val categories by viewModel.categories.collectAsState()

    Scaffold { padding ->
        Column(modifier = Modifier.fillMaxSize().padding(padding).padding(24.dp)) {
            Text(
                text = "Thematic Learning",
                style = MaterialTheme.typography.headlineMedium,
                modifier = Modifier.padding(bottom = 4.dp)
            )
            Text(
                text = "3 new words unlock per category every day.",
                style = MaterialTheme.typography.bodyMedium,
                modifier = Modifier.padding(bottom = 24.dp)
            )
            LazyColumn {
                items(categories, key = { it.category }) { summary ->
                    CategoryRow(summary, onClick = { onOpenCategory(summary.category) })
                }
            }
        }
    }
}

@Composable
private fun CategoryRow(summary: CategorySummary, onClick: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp)
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surfaceVariant)
            .clickable(onClick = onClick)
            .padding(16.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(text = displayName(summary.category), style = MaterialTheme.typography.titleMedium)
            Text(
                text = "${summary.unlockedCount} / ${summary.totalWords}",
                style = MaterialTheme.typography.bodyMedium
            )
        }
        LinearProgressIndicator(
            progress = {
                if (summary.totalWords == 0) 0f else summary.unlockedCount / summary.totalWords.toFloat()
            },
            modifier = Modifier.fillMaxWidth().padding(top = 8.dp)
        )
    }
}
