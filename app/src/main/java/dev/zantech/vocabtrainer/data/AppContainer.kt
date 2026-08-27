package dev.zantech.vocabtrainer.data

import android.content.Context

/**
 * Manual dependency container. Deliberately not using Hilt/Koin — the app has one
 * repository and no scoping needs, see CLAUDE.md §3.
 */
class AppContainer(context: Context) {
    private val database = AppDatabase.getInstance(context)

    val repository: VocabRepository = VocabRepository(
        context = context.applicationContext,
        wordDao = database.wordDao(),
        appStateDao = database.appStateDao(),
        conjugationDao = database.conjugationDao(),
        thematicDao = database.thematicDao()
    )
}
