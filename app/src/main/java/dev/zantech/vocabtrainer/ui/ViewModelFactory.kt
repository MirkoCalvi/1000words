package dev.zantech.vocabtrainer.ui

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewmodel.CreationExtras
import dev.zantech.vocabtrainer.data.VocabRepository
import dev.zantech.vocabtrainer.ui.conjugation.ConjugationViewModel
import dev.zantech.vocabtrainer.ui.flashcard.FlashcardViewModel
import dev.zantech.vocabtrainer.ui.home.HomeViewModel
import dev.zantech.vocabtrainer.ui.quiz.QuizViewModel
import dev.zantech.vocabtrainer.ui.sentence.SentenceViewModel
import dev.zantech.vocabtrainer.ui.thematic.ThematicListViewModel

/**
 * Manual ViewModel factory (no Hilt, see CLAUDE.md §3). One factory covers all three
 * screens since each ViewModel only needs the shared [VocabRepository].
 */
class ViewModelFactory(val repository: VocabRepository) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>, extras: CreationExtras): T =
        when (modelClass) {
            HomeViewModel::class.java -> HomeViewModel(repository)
            FlashcardViewModel::class.java -> FlashcardViewModel(repository)
            QuizViewModel::class.java -> QuizViewModel(repository)
            ConjugationViewModel::class.java -> ConjugationViewModel(repository)
            SentenceViewModel::class.java -> SentenceViewModel(repository)
            ThematicListViewModel::class.java -> ThematicListViewModel(repository)
            else -> throw IllegalArgumentException("Unknown ViewModel class: $modelClass")
        } as T
}
