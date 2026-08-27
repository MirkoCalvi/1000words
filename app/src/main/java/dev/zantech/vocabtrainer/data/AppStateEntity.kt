package dev.zantech.vocabtrainer.data

import androidx.room.Entity
import androidx.room.PrimaryKey

/** Single-row table holding the daily streak state. Always keyed at id = 0. */
@Entity(tableName = "app_state")
data class AppStateEntity(
    @PrimaryKey val id: Int = 0,
    val currentStreak: Int = 0,
    val lastPracticeDate: String? = null // ISO-8601 date (yyyy-MM-dd), device local date
)
