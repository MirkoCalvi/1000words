package dev.zantech.vocabtrainer.data

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Present + preterite conjugation for one verb (wordId references WordEntity.id).
 * One row per verb, six-person forms flattened into columns rather than a child
 * table — simplest shape for what's just a lookup table read wholesale per verb.
 */
@Entity(tableName = "conjugations")
data class ConjugationEntity(
    @PrimaryKey val wordId: Int,
    val presentYo: String,
    val presentTu: String,
    val presentEl: String,
    val presentNosotros: String,
    val presentVosotros: String,
    val presentEllos: String,
    val preteriteYo: String,
    val preteriteTu: String,
    val preteriteEl: String,
    val preteriteNosotros: String,
    val preteriteVosotros: String,
    val preteriteEllos: String
)

enum class Tense { PRESENT, PRETERITE }

enum class Person(val label: String) {
    YO("yo"), TU("tú"), EL("él/ella"), NOSOTROS("nosotros"), VOSOTROS("vosotros"), ELLOS("ellos/ellas")
}

fun ConjugationEntity.formFor(tense: Tense, person: Person): String = when (tense) {
    Tense.PRESENT -> when (person) {
        Person.YO -> presentYo
        Person.TU -> presentTu
        Person.EL -> presentEl
        Person.NOSOTROS -> presentNosotros
        Person.VOSOTROS -> presentVosotros
        Person.ELLOS -> presentEllos
    }
    Tense.PRETERITE -> when (person) {
        Person.YO -> preteriteYo
        Person.TU -> preteriteTu
        Person.EL -> preteriteEl
        Person.NOSOTROS -> preteriteNosotros
        Person.VOSOTROS -> preteriteVosotros
        Person.ELLOS -> preteriteEllos
    }
}

fun ConjugationEntity.allForms(tense: Tense): List<Pair<Person, String>> =
    Person.entries.map { it to formFor(tense, it) }
