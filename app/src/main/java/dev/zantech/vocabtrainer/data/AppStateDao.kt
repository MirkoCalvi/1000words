package dev.zantech.vocabtrainer.data

import androidx.room.Dao
import androidx.room.Query
import androidx.room.Upsert
import kotlinx.coroutines.flow.Flow

@Dao
interface AppStateDao {

    @Query("SELECT * FROM app_state WHERE id = 0")
    fun observe(): Flow<AppStateEntity?>

    @Query("SELECT * FROM app_state WHERE id = 0")
    suspend fun get(): AppStateEntity?

    @Upsert
    suspend fun upsert(state: AppStateEntity)
}
