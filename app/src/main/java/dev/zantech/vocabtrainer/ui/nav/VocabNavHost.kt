package dev.zantech.vocabtrainer.ui.nav

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import dev.zantech.vocabtrainer.ui.ViewModelFactory
import dev.zantech.vocabtrainer.ui.conjugation.ConjugationScreen
import dev.zantech.vocabtrainer.ui.flashcard.FlashcardScreen
import dev.zantech.vocabtrainer.ui.home.HomeScreen
import dev.zantech.vocabtrainer.ui.quiz.QuizScreen
import dev.zantech.vocabtrainer.ui.sentence.SentenceScreen
import dev.zantech.vocabtrainer.ui.thematic.ThematicCategoryScreen
import dev.zantech.vocabtrainer.ui.thematic.ThematicListScreen

private object Routes {
    const val HOME = "home"
    const val FLASHCARDS = "flashcards"
    const val QUIZ = "quiz"
    const val CONJUGATE = "conjugate"
    const val SENTENCE = "sentence"
    const val THEMATIC = "thematic"
    const val THEMATIC_CATEGORY = "thematic/{category}"
}

/** The app's navigation graph, see CLAUDE.md §4. */
@Composable
fun VocabNavHost(
    viewModelFactory: ViewModelFactory,
    navController: NavHostController = rememberNavController()
) {
    NavHost(navController = navController, startDestination = Routes.HOME) {
        composable(Routes.HOME) {
            HomeScreen(
                viewModelFactory = viewModelFactory,
                onPracticeFlashcards = { navController.navigate(Routes.FLASHCARDS) },
                onTakeQuiz = { navController.navigate(Routes.QUIZ) },
                onConjugateVerbs = { navController.navigate(Routes.CONJUGATE) },
                onCompleteSentence = { navController.navigate(Routes.SENTENCE) },
                onThematicLearning = { navController.navigate(Routes.THEMATIC) }
            )
        }
        composable(Routes.FLASHCARDS) {
            FlashcardScreen(
                viewModelFactory = viewModelFactory,
                onSessionComplete = { navController.popBackStack(Routes.HOME, inclusive = false) }
            )
        }
        composable(Routes.QUIZ) {
            QuizScreen(
                viewModelFactory = viewModelFactory,
                onSessionComplete = { navController.popBackStack(Routes.HOME, inclusive = false) }
            )
        }
        composable(Routes.CONJUGATE) {
            ConjugationScreen(
                viewModelFactory = viewModelFactory,
                onSessionComplete = { navController.popBackStack(Routes.HOME, inclusive = false) }
            )
        }
        composable(Routes.SENTENCE) {
            SentenceScreen(
                viewModelFactory = viewModelFactory,
                onSessionComplete = { navController.popBackStack(Routes.HOME, inclusive = false) }
            )
        }
        composable(Routes.THEMATIC) {
            ThematicListScreen(
                viewModelFactory = viewModelFactory,
                onOpenCategory = { category -> navController.navigate("thematic/$category") }
            )
        }
        composable(
            route = Routes.THEMATIC_CATEGORY,
            arguments = listOf(navArgument("category") { type = NavType.StringType })
        ) { backStackEntry ->
            val category = backStackEntry.arguments?.getString("category").orEmpty()
            ThematicCategoryScreen(
                category = category,
                viewModelFactory = viewModelFactory,
                onBack = { navController.popBackStack() }
            )
        }
    }
}
