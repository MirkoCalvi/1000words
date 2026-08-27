package dev.zantech.vocabtrainer.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query

@Dao
interface ConjugationDao {

    @Insert(onConflict = OnConflictStrategy.IGNORE)
    suspend fun insertAll(conjugations: List<ConjugationEntity>)

    @Query("SELECT COUNT(*) FROM conjugations")
    suspend fun count(): Int

    /** A random verb (joined with its word row) that has a conjugation entry. */
    @Query(
        "SELECT words.* FROM words INNER JOIN conjugations ON words.id = conjugations.wordId " +
            "ORDER BY RANDOM() LIMIT :limit"
    )
    suspend fun randomConjugatedWords(limit: Int): List<WordEntity>

    @Query("SELECT * FROM conjugations WHERE wordId = :wordId")
    suspend fun forWord(wordId: Int): ConjugationEntity?

    @Query(
        "SELECT conjugations.* FROM conjugations INNER JOIN words ON words.id = conjugations.wordId " +
            "WHERE words.id != :excludeWordId ORDER BY RANDOM() LIMIT :limit"
    )
    suspend fun randomOtherConjugations(excludeWordId: Int, limit: Int): List<ConjugationEntity>
}
