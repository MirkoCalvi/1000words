package dev.zantech.vocabtrainer.data

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Tracks the daily word-unlock drip for one thematic category. `unlockedCount`
 * is cumulative — it only grows, by up to 3 per new calendar day (see CLAUDE.md
 * §5's thematic-learning spec). The first `unlockedCount` words of that
 * category (by id order) are the ones currently visible to the user.
 */
@Entity(tableName = "thematic_progress")
data class ThematicProgressEntity(
    @PrimaryKey val category: String,
    val unlockedCount: Int = 0,
    val lastUnlockDate: String? = null // ISO-8601 date
)
