package dev.zantech.vocabtrainer.ui.thematic

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dev.zantech.vocabtrainer.data.CategorySummary
import dev.zantech.vocabtrainer.data.VocabRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class ThematicListViewModel(private val repository: VocabRepository) : ViewModel() {

    private val _categories = MutableStateFlow<List<CategorySummary>>(emptyList())
    val categories: StateFlow<List<CategorySummary>> = _categories.asStateFlow()

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            repository.ensureDailyThematicUnlock()
            _categories.value = repository.categorySummaries()
        }
    }
}
