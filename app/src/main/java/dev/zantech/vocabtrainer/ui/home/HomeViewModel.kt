package dev.zantech.vocabtrainer.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dev.zantech.vocabtrainer.data.HomeState
import dev.zantech.vocabtrainer.data.VocabRepository
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class HomeViewModel(private val repository: VocabRepository) : ViewModel() {

    val state: StateFlow<HomeState> = repository.homeState()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = HomeState(currentStreak = 0, masteredCount = 0, totalCount = 0)
        )

    init {
        viewModelScope.launch {
            repository.seedIfEmpty()
            // Runs on every Home visit; no-ops after the first check today per category.
            repository.ensureDailyThematicUnlock()
        }
    }
}
