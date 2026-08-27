package dev.zantech.vocabtrainer.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

@Database(
    entities = [
        WordEntity::class, AppStateEntity::class,
        ConjugationEntity::class, ThematicProgressEntity::class
    ],
    version = 2,
    exportSchema = true
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun wordDao(): WordDao
    abstract fun appStateDao(): AppStateDao
    abstract fun conjugationDao(): ConjugationDao
    abstract fun thematicDao(): ThematicDao

    companion object {
        @Volatile
        private var instance: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase =
            instance ?: synchronized(this) {
                instance ?: Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "vocab_trainer.db"
                )
                    // No released users yet (see CLAUDE.md) — a destructive migration is
                    // simpler than writing real Migration objects for a schema still in flux.
                    .fallbackToDestructiveMigration()
                    .build().also { instance = it }
            }
    }
}
