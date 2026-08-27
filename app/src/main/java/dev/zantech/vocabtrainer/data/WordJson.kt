package dev.zantech.vocabtrainer.data

import android.content.Context
import org.json.JSONArray

/** Plain shape of one entry in assets/words.json. */
data class WordJson(
    val id: Int,
    val spanish: String,
    val english: String,
    val partOfSpeech: String,
    val example: String,
    val category: String
)

/**
 * Reads assets/words.json. No third-party JSON library needed — org.json ships with
 * Android, and the schema is small enough that manual parsing stays simple.
 */
object WordJsonLoader {

    fun load(context: Context, assetName: String = "words.json"): List<WordJson> {
        val text = context.assets.open(assetName).bufferedReader().use { it.readText() }
        val array = JSONArray(text)
        return buildList(array.length()) {
            for (i in 0 until array.length()) {
                val obj = array.getJSONObject(i)
                add(
                    WordJson(
                        id = obj.getInt("id"),
                        spanish = obj.getString("spanish"),
                        english = obj.getString("english"),
                        partOfSpeech = obj.getString("partOfSpeech"),
                        example = obj.getString("example"),
                        category = obj.getString("category")
                    )
                )
            }
        }
    }
}

/** Plain shape of one entry in assets/conjugations.json. */
data class ConjugationJson(
    val wordId: Int,
    val present: Map<String, String>,
    val preterite: Map<String, String>
)

object ConjugationJsonLoader {

    fun load(context: Context, assetName: String = "conjugations.json"): List<ConjugationJson> {
        val text = context.assets.open(assetName).bufferedReader().use { it.readText() }
        val array = JSONArray(text)
        return buildList(array.length()) {
            for (i in 0 until array.length()) {
                val obj = array.getJSONObject(i)
                add(
                    ConjugationJson(
                        wordId = obj.getInt("wordId"),
                        present = obj.getJSONObject("present").toStringMap(),
                        preterite = obj.getJSONObject("preterite").toStringMap()
                    )
                )
            }
        }
    }

    private fun org.json.JSONObject.toStringMap(): Map<String, String> {
        val map = LinkedHashMap<String, String>()
        keys().asSequence().forEach { key -> map[key] = getString(key) }
        return map
    }
}
