package dev.zantech.vocabtrainer.data

import android.content.Context
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import java.time.LocalDate
import java.time.format.DateTimeFormatter

/** How many consecutive correct answers mark a word as mastered (placeholder, see CLAUDE.md §10). */
private const val MASTERY_STREAK_THRESHOLD = 3

/** Words shown per flashcard/quiz/conjugation/sentence session. */
const val SESSION_BATCH_SIZE = 20

/** Multiple-choice options per question (1 correct + 3 distractors). */
const val QUIZ_CHOICE_COUNT = 4

/** New words unlocked per thematic category per calendar day (see CLAUDE.md §5). */
const val THEMATIC_DAILY_UNLOCK = 3

private val ISO = DateTimeFormatter.ISO_LOCAL_DATE

data class HomeState(val currentStreak: Int, val masteredCount: Int, val totalCount: Int)

data class ConjugationQuestion(
    val word: WordEntity,
    val tense: Tense,
    val person: Person,
    val correctForm: String,
    val choices: List<String>
)

data class SentenceQuestion(
    val word: WordEntity,
    val blankedSentence: String,
    val choices: List<WordEntity>
)

data class CategorySummary(
    val category: String,
    val totalWords: Int,
    val unlockedCount: Int
)

/**
 * Single access point for word + streak + conjugation + thematic data. Kept as one
 * class (no DI framework) per CLAUDE.md §3.
 */
class VocabRepository(
    private val context: Context,
    private val wordDao: WordDao,
    private val appStateDao: AppStateDao,
    private val conjugationDao: ConjugationDao,
    private val thematicDao: ThematicDao
) {

    /** Populates Room from the bundled assets the first time the app runs. No-op after that. */
    suspend fun seedIfEmpty() {
        if (wordDao.count() > 0) return
        val words = WordJsonLoader.load(context).map {
            WordEntity(
                id = it.id,
                spanish = it.spanish,
                english = it.english,
                partOfSpeech = it.partOfSpeech,
                example = it.example,
                category = it.category
            )
        }
        wordDao.insertAll(words)

        val conjugations = ConjugationJsonLoader.load(context).map {
            ConjugationEntity(
                wordId = it.wordId,
                presentYo = it.present.getValue("yo"),
                presentTu = it.present.getValue("tu"),
                presentEl = it.present.getValue("el"),
                presentNosotros = it.present.getValue("nosotros"),
                presentVosotros = it.present.getValue("vosotros"),
                presentEllos = it.present.getValue("ellos"),
                preteriteYo = it.preterite.getValue("yo"),
                preteriteTu = it.preterite.getValue("tu"),
                preteriteEl = it.preterite.getValue("el"),
                preteriteNosotros = it.preterite.getValue("nosotros"),
                preteriteVosotros = it.preterite.getValue("vosotros"),
                preteriteEllos = it.preterite.getValue("ellos")
            )
        }
        conjugationDao.insertAll(conjugations)
    }

    fun homeState(): Flow<HomeState> =
        combine(appStateDao.observe(), wordDao.masteredCountFlow(), wordDao.totalCountFlow()) {
            state, mastered, total ->
            HomeState(
                currentStreak = state?.currentStreak ?: 0,
                masteredCount = mastered,
                totalCount = total
            )
        }

    suspend fun flashcardBatch(): List<WordEntity> = wordDao.randomBatch(SESSION_BATCH_SIZE)

    suspend fun quizBatch(): List<WordEntity> = wordDao.randomBatch(SESSION_BATCH_SIZE)

    /** Correct answer + 3 same-part-of-speech distractors, all shuffled together. */
    suspend fun quizChoicesFor(word: WordEntity): List<WordEntity> {
        val distractors = wordDao.randomDistractors(
            partOfSpeech = word.partOfSpeech,
            excludeId = word.id,
            limit = QUIZ_CHOICE_COUNT - 1
        )
        return (listOf(word) + distractors).shuffled()
    }

    /** Records a flashcard self-rating ("Got it" / "Still learning") and updates mastery. */
    suspend fun recordFlashcardResult(word: WordEntity, gotIt: Boolean) {
        applyResult(word, correct = gotIt)
    }

    /** Records a quiz answer and updates mastery. */
    suspend fun recordQuizResult(word: WordEntity, correct: Boolean) {
        applyResult(word, correct = correct)
    }

    private suspend fun applyResult(word: WordEntity, correct: Boolean) {
        val newStreak = if (correct) word.correctStreak + 1 else 0
        val updated = word.copy(
            timesCorrect = word.timesCorrect + if (correct) 1 else 0,
            timesIncorrect = word.timesIncorrect + if (correct) 0 else 1,
            correctStreak = newStreak,
            mastered = word.mastered || newStreak >= MASTERY_STREAK_THRESHOLD
        )
        wordDao.update(updated)
    }

    /** Call once at the end of any completed session (flashcard/quiz/conjugation/sentence). */
    suspend fun recordSessionCompleted() {
        val today = LocalDate.now()
        val todayIso = today.format(ISO)
        val state = appStateDao.get()
        val lastDate = state?.lastPracticeDate?.let { runCatching { LocalDate.parse(it) }.getOrNull() }

        val newStreak = when {
            lastDate == today -> state?.currentStreak ?: 1 // already practiced today, no change
            lastDate == today.minusDays(1) -> (state?.currentStreak ?: 0) + 1
            else -> 1 // gap of 2+ days, or first ever session
        }

        appStateDao.upsert(AppStateEntity(currentStreak = newStreak, lastPracticeDate = todayIso))
    }

    // -- Conjugate Verbs ----------------------------------------------------

    suspend fun conjugationBatch(): List<ConjugationQuestion> {
        val verbs = conjugationDao.randomConjugatedWords(SESSION_BATCH_SIZE)
        return verbs.mapNotNull { word ->
            val entity = conjugationDao.forWord(word.id) ?: return@mapNotNull null
            val tense = Tense.entries.random()
            val person = Person.entries.random()
            val correct = entity.formFor(tense, person)
            val distractors = entity.allForms(tense)
                .filter { it.first != person }
                .map { it.second }
                .distinct()
                .shuffled()
                .take(QUIZ_CHOICE_COUNT - 1)
            ConjugationQuestion(
                word = word,
                tense = tense,
                person = person,
                correctForm = correct,
                choices = (distractors + correct).shuffled()
            )
        }
    }

    // -- Complete the Sentence ------------------------------------------------

    suspend fun sentenceBatch(): List<SentenceQuestion> {
        val candidates = wordDao.randomSentenceCandidates(SESSION_BATCH_SIZE)
        return candidates.map { word ->
            val blankRegex = Regex("\\b${Regex.escape(word.spanish)}\\b", RegexOption.IGNORE_CASE)
            val blanked = blankRegex.replaceFirst(word.example, "_____")
            SentenceQuestion(
                word = word,
                blankedSentence = blanked,
                choices = quizChoicesFor(word)
            )
        }
    }

    // -- Thematic Learning ----------------------------------------------------

    /** Unlocks up to [THEMATIC_DAILY_UNLOCK] new words per category, once per calendar day. */
    suspend fun ensureDailyThematicUnlock() {
        val today = LocalDate.now().format(ISO)
        val counts = thematicDao.categoryCounts()
        for ((category, total) in counts.map { it.category to it.total }) {
            val progress = thematicDao.get(category)
            if (progress?.lastUnlockDate == today) continue
            val newCount = minOf((progress?.unlockedCount ?: 0) + THEMATIC_DAILY_UNLOCK, total)
            thematicDao.upsert(ThematicProgressEntity(category, newCount, today))
        }
    }

    /** Category totals are static (assigned at seed time); progress is re-read on demand
     * rather than observed as a Flow — simplest given how infrequently it changes (once
     * per category per day). */
    suspend fun categorySummaries(): List<CategorySummary> {
        val counts = thematicDao.categoryCounts()
        return counts.map { (category, total) ->
            val progress = thematicDao.get(category)
            CategorySummary(category, totalWords = total, unlockedCount = progress?.unlockedCount ?: 0)
        }
    }

    suspend fun unlockedWordsIn(category: String): List<WordEntity> {
        val progress = thematicDao.get(category)
        return thematicDao.unlockedWords(category, progress?.unlockedCount ?: 0)
    }
}
