package dev.zantech.vocabtrainer.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import kotlinx.coroutines.flow.Flow

@Dao
interface WordDao {

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertAll(words: List<WordEntity>)

    @Query("SELECT COUNT(*) FROM words")
    suspend fun count(): Int

    @Query("SELECT COUNT(*) FROM words WHERE mastered = 1")
    fun masteredCountFlow(): Flow<Int>

    @Query("SELECT COUNT(*) FROM words")
    fun totalCountFlow(): Flow<Int>

    /** Random batch of words for a flashcard or quiz session. */
    @Query("SELECT * FROM words ORDER BY RANDOM() LIMIT :limit")
    suspend fun randomBatch(limit: Int): List<WordEntity>

    /** Distractor pool: words with the same part of speech, excluding the correct one. */
    @Query(
        "SELECT * FROM words WHERE partOfSpeech = :partOfSpeech AND id != :excludeId " +
            "ORDER BY RANDOM() LIMIT :limit"
    )
    suspend fun randomDistractors(partOfSpeech: String, excludeId: Int, limit: Int): List<WordEntity>

    /** Words whose example sentence literally contains their own spanish word — the
     * only ones a "complete the sentence" blank can be built from safely. */
    @Query(
        "SELECT * FROM words WHERE example LIKE '%' || spanish || '%' " +
            "ORDER BY RANDOM() LIMIT :limit"
    )
    suspend fun randomSentenceCandidates(limit: Int): List<WordEntity>

    @Update
    suspend fun update(word: WordEntity)
}
