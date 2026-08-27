package dev.zantech.vocabtrainer.ui.conjugation

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dev.zantech.vocabtrainer.data.ConjugationQuestion
import dev.zantech.vocabtrainer.data.VocabRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class ConjugationUiState(
    val questions: List<ConjugationQuestion> = emptyList(),
    val index: Int = 0,
    val selected: String? = null,
    val sessionComplete: Boolean = false
) {
    val current: ConjugationQuestion? get() = questions.getOrNull(index)
    val answered: Boolean get() = selected != null
}

/** "Conjugate Verbs" session, see CLAUDE.md §4. */
class ConjugationViewModel(private val repository: VocabRepository) : ViewModel() {

    private val _state = MutableStateFlow(ConjugationUiState())
    val state: StateFlow<ConjugationUiState> = _state.asStateFlow()

    init {
        viewModelScope.launch {
            _state.value = ConjugationUiState(questions = repository.conjugationBatch())
        }
    }

    fun selectAnswer(choice: String) {
        if (_state.value.answered) return
        val question = _state.value.current ?: return
        _state.value = _state.value.copy(selected = choice)
        viewModelScope.launch {
            repository.recordQuizResult(question.word, correct = choice == question.correctForm)
        }
    }

    fun next() {
        viewModelScope.launch {
            val nextIndex = _state.value.index + 1
            if (nextIndex >= _state.value.questions.size) {
                repository.recordSessionCompleted()
                _state.value = _state.value.copy(sessionComplete = true)
            } else {
                _state.value = _state.value.copy(index = nextIndex, selected = null)
            }
        }
    }
}
