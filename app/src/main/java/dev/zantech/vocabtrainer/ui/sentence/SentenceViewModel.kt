package dev.zantech.vocabtrainer.ui.sentence

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import dev.zantech.vocabtrainer.data.SentenceQuestion
import dev.zantech.vocabtrainer.data.VocabRepository
import dev.zantech.vocabtrainer.data.WordEntity
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class SentenceUiState(
    val questions: List<SentenceQuestion> = emptyList(),
    val index: Int = 0,
    val selectedId: Int? = null,
    val sessionComplete: Boolean = false
) {
    val current: SentenceQuestion? get() = questions.getOrNull(index)
    val answered: Boolean get() = selectedId != null
}

/** "Complete the Sentence" session, see CLAUDE.md §4. */
class SentenceViewModel(private val repository: VocabRepository) : ViewModel() {

    private val _state = MutableStateFlow(SentenceUiState())
    val state: StateFlow<SentenceUiState> = _state.asStateFlow()

    init {
        viewModelScope.launch {
            _state.value = SentenceUiState(questions = repository.sentenceBatch())
        }
    }

    fun selectAnswer(choice: WordEntity) {
        if (_state.value.answered) return
        val question = _state.value.current ?: return
        _state.value = _state.value.copy(selectedId = choice.id)
        viewModelScope.launch {
            repository.recordQuizResult(question.word, correct = choice.id == question.word.id)
        }
    }

    fun next() {
        viewModelScope.launch {
            val nextIndex = _state.value.index + 1
            if (nextIndex >= _state.value.questions.size) {
                repository.recordSessionCompleted()
                _state.value = _state.value.copy(sessionComplete = true)
            } else {
                _state.value = _state.value.copy(index = nextIndex, selectedId = null)
            }
        }
    }
}
