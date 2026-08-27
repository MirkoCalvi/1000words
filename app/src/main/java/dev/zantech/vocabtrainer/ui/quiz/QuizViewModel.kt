package dev.zantech.vocabtrainer.ui.quiz

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dev.zantech.vocabtrainer.data.VocabRepository
import dev.zantech.vocabtrainer.data.WordEntity
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class QuizUiState(
    val words: List<WordEntity> = emptyList(),
    val index: Int = 0,
    val choices: List<WordEntity> = emptyList(),
    val selectedId: Int? = null,
    val sessionComplete: Boolean = false
) {
    val currentWord: WordEntity? get() = words.getOrNull(index)
    val answered: Boolean get() = selectedId != null
}

class QuizViewModel(private val repository: VocabRepository) : ViewModel() {

    private val _state = MutableStateFlow(QuizUiState())
    val state: StateFlow<QuizUiState> = _state.asStateFlow()

    init {
        viewModelScope.launch {
            val batch = repository.quizBatch()
            _state.value = QuizUiState(words = batch)
            loadChoicesForCurrent()
        }
    }

    private suspend fun loadChoicesForCurrent() {
        val word = _state.value.currentWord ?: return
        val choices = repository.quizChoicesFor(word)
        _state.value = _state.value.copy(choices = choices)
    }

    fun selectAnswer(choice: WordEntity) {
        val current = _state.value.currentWord ?: return
        if (_state.value.answered) return // ignore taps after the first answer
        _state.value = _state.value.copy(selectedId = choice.id)
        viewModelScope.launch {
            repository.recordQuizResult(current, correct = choice.id == current.id)
        }
    }

    fun next() {
        viewModelScope.launch {
            val nextIndex = _state.value.index + 1
            if (nextIndex >= _state.value.words.size) {
                repository.recordSessionCompleted()
                _state.value = _state.value.copy(sessionComplete = true)
            } else {
                _state.value = _state.value.copy(index = nextIndex, selectedId = null, choices = emptyList())
                loadChoicesForCurrent()
            }
        }
    }
}
