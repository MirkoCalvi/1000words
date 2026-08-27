package dev.zantech.vocabtrainer.ui.flashcard

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dev.zantech.vocabtrainer.data.VocabRepository
import dev.zantech.vocabtrainer.data.WordEntity
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class FlashcardUiState(
    val words: List<WordEntity> = emptyList(),
    val index: Int = 0,
    val revealed: Boolean = false,
    val sessionComplete: Boolean = false
) {
    val currentWord: WordEntity? get() = words.getOrNull(index)
}

class FlashcardViewModel(private val repository: VocabRepository) : ViewModel() {

    private val _state = MutableStateFlow(FlashcardUiState())
    val state: StateFlow<FlashcardUiState> = _state.asStateFlow()

    init {
        viewModelScope.launch {
            val batch = repository.flashcardBatch()
            _state.value = FlashcardUiState(words = batch)
        }
    }

    fun reveal() {
        _state.value = _state.value.copy(revealed = true)
    }

    /** "Got it" (gotIt = true) or "Still learning" (gotIt = false). */
    fun answer(gotIt: Boolean) {
        val current = _state.value.currentWord ?: return
        viewModelScope.launch {
            repository.recordFlashcardResult(current, gotIt)
            advance()
        }
    }

    private fun advance() {
        val next = _state.value.index + 1
        if (next >= _state.value.words.size) {
            viewModelScope.launch { repository.recordSessionCompleted() }
            _state.value = _state.value.copy(sessionComplete = true)
        } else {
            _state.value = _state.value.copy(index = next, revealed = false)
        }
    }
}
