package dev.zantech.vocabtrainer

import android.app.Application
import dev.zantech.vocabtrainer.data.AppContainer

class VocabTrainerApp : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)
    }
}
