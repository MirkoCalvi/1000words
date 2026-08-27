package dev.zantech.vocabtrainer.data

import androidx.room.Dao
import androidx.room.Query
import androidx.room.Upsert
import kotlinx.coroutines.flow.Flow

data class CategoryCount(val category: String, val total: Int)

@Dao
interface ThematicDao {

    @Query("SELECT DISTINCT category FROM words ORDER BY category")
    suspend fun allCategories(): List<String>

    @Query("SELECT category, COUNT(*) as total FROM words GROUP BY category ORDER BY category")
    suspend fun categoryCounts(): List<CategoryCount>

    @Query("SELECT * FROM thematic_progress")
    fun observeAll(): Flow<List<ThematicProgressEntity>>

    @Query("SELECT * FROM thematic_progress WHERE category = :category")
    suspend fun get(category: String): ThematicProgressEntity?

    @Upsert
    suspend fun upsert(progress: ThematicProgressEntity)

    /** The words currently unlocked in a category, ordered by id (oldest-unlocked first). */
    @Query("SELECT * FROM words WHERE category = :category ORDER BY id LIMIT :unlockedCount")
    suspend fun unlockedWords(category: String, unlockedCount: Int): List<WordEntity>
}
