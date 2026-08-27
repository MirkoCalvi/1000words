package dev.zantech.vocabtrainer.data

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * One vocabulary word plus its per-word learning state.
 *
 * `id` mirrors the id in the bundled words.json asset so re-seeding (if the app is
 * ever reinstalled) lines up with the same word again.
 */
@Entity(tableName = "words")
data class WordEntity(
    @PrimaryKey val id: Int,
    val spanish: String,
    val english: String,
    val partOfSpeech: String, // "noun" | "verb"
    val example: String,
    val category: String = "general", // thematic bucket, e.g. "house", "travel" — see CLAUDE.md §5
    val timesCorrect: Int = 0,
    val timesIncorrect: Int = 0,
    val correctStreak: Int = 0, // consecutive correct answers, used for the "mastered" threshold
    val mastered: Boolean = false
)
