#!/usr/bin/env python3
"""
Generates app/src/main/assets/words.json and app/src/main/assets/conjugations.json
from the curated word lists below.

Not part of the Kotlin build — run manually whenever the word list changes:
    python3 tools/generate_words.py

Why a generator instead of hand-typed JSON: conjugating ~250 verbs across two
tenses by hand is both huge and error-prone. This applies real conjugation
rules (regular endings, stem-changing patterns, an irregular-verb override
table) so the output is consistent, and builds example sentences from a small
set of grammatically-safe templates instead of one-off hand-written sentences
for all 1000 entries.
"""
import json
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "app", "src", "main", "assets")

# ---------------------------------------------------------------------------
# Conjugation engine
# ---------------------------------------------------------------------------

PERSONS = ["yo", "tu", "el", "nosotros", "vosotros", "ellos"]

PRESENT_ENDINGS = {
    "ar": ["o", "as", "a", "amos", "áis", "an"],
    "er": ["o", "es", "e", "emos", "éis", "en"],
    "ir": ["o", "es", "e", "imos", "ís", "en"],
}
PRETERITE_ENDINGS = {
    "ar": ["é", "aste", "ó", "amos", "asteis", "aron"],
    "er": ["í", "iste", "ió", "imos", "isteis", "ieron"],
    "ir": ["í", "iste", "ió", "imos", "isteis", "ieron"],
}

# Fully irregular present tense (doesn't fit any rule below).
IRREGULAR_PRESENT = {
    "ser": ["soy", "eres", "es", "somos", "sois", "son"],
    "estar": ["estoy", "estás", "está", "estamos", "estáis", "están"],
    "ir": ["voy", "vas", "va", "vamos", "vais", "van"],
    "haber": ["he", "has", "ha", "hemos", "habéis", "han"],
    "tener": ["tengo", "tienes", "tiene", "tenemos", "tenéis", "tienen"],
    "hacer": ["hago", "haces", "hace", "hacemos", "hacéis", "hacen"],
    "decir": ["digo", "dices", "dice", "decimos", "decís", "dicen"],
    "poner": ["pongo", "pones", "pone", "ponemos", "ponéis", "ponen"],
    "salir": ["salgo", "sales", "sale", "salimos", "salís", "salen"],
    "venir": ["vengo", "vienes", "viene", "venimos", "venís", "vienen"],
    "saber": ["sé", "sabes", "sabe", "sabemos", "sabéis", "saben"],
    "ver": ["veo", "ves", "ve", "vemos", "veis", "ven"],
    "dar": ["doy", "das", "da", "damos", "dais", "dan"],
    "oír": ["oigo", "oyes", "oye", "oímos", "oís", "oyen"],
    "traer": ["traigo", "traes", "trae", "traemos", "traéis", "traen"],
    "caber": ["quepo", "cabes", "cabe", "cabemos", "cabéis", "caben"],
    "valer": ["valgo", "vales", "vale", "valemos", "valéis", "valen"],
    "caer": ["caigo", "caes", "cae", "caemos", "caéis", "caen"],
    # -eír verbs: accent pattern doesn't fit the generic e:i stem-change rule.
    "reír": ["río", "ríes", "ríe", "reímos", "reís", "ríen"],
    "sonreír": ["sonrío", "sonríes", "sonríe", "sonreímos", "sonreís", "sonríen"],
}

# Fully irregular preterite (doesn't fit the j-stem / regular pattern below).
IRREGULAR_PRETERITE = {
    "ser": ["fui", "fuiste", "fue", "fuimos", "fuisteis", "fueron"],
    "ir": ["fui", "fuiste", "fue", "fuimos", "fuisteis", "fueron"],
    "dar": ["di", "diste", "dio", "dimos", "disteis", "dieron"],
    "ver": ["vi", "viste", "vio", "vimos", "visteis", "vieron"],
    "reír": ["reí", "reíste", "rio", "reímos", "reísteis", "rieron"],
    "sonreír": ["sonreí", "sonreíste", "sonrio", "sonreímos", "sonreísteis", "sonrieron"],
}

# -er/-ir verbs whose preterite stem changes but keeps regular-ish endings.
PRETERITE_STEM_IRREGULAR = {
    "tener": "tuv", "estar": "estuv", "andar": "anduv", "poder": "pud",
    "poner": "pus", "saber": "sup", "caber": "cup", "querer": "quis",
    "venir": "vin", "hacer": "hic",
}
# These use -e,-iste,-o,-imos,-isteis,-ieron but "hacer" 3rd person is "hizo" (c->z).
PRETERITE_IRREGULAR_ENDINGS = ["e", "iste", "o", "imos", "isteis", "ieron"]

# -j- preterite stems (3rd plural ending is "-eron", not "-ieron").
PRETERITE_J_STEM = {
    "decir": "dij", "traer": "traj", "conducir": "conduj",
    "producir": "produj", "traducir": "traduj",
}
PRETERITE_J_ENDINGS = ["e", "iste", "o", "imos", "isteis", "eron"]

# Present-tense stem-changing verbs: infinitive -> pattern. Affects yo/tu/el/ellos,
# not nosotros/vosotros. Skipped for verbs already in IRREGULAR_PRESENT.
STEM_CHANGE_PRESENT = {
    "querer": "e:ie", "pensar": "e:ie", "empezar": "e:ie", "entender": "e:ie",
    "sentir": "e:ie", "preferir": "e:ie", "cerrar": "e:ie", "perder": "e:ie",
    "comenzar": "e:ie", "defender": "e:ie", "encender": "e:ie", "mentir": "e:ie",
    "despertar": "e:ie", "negar": "e:ie", "sentar": "e:ie", "sugerir": "e:ie",
    "poder": "o:ue", "volver": "o:ue", "encontrar": "o:ue", "dormir": "o:ue",
    "morir": "o:ue", "contar": "o:ue", "mostrar": "o:ue", "recordar": "o:ue",
    "resolver": "o:ue", "soñar": "o:ue", "sonar": "o:ue", "soltar": "o:ue",
    "devolver": "o:ue", "probar": "o:ue", "rogar": "o:ue",
    "jugar": "u:ue",
    "pedir": "e:i", "servir": "e:i", "seguir": "e:i", "repetir": "e:i",
    "elegir": "e:i", "medir": "e:i",
    "perseguir": "e:i", "vestir": "e:i", "despedir": "e:i", "conseguir": "e:i",
}
# -guir verbs drop the "u" before an "o" ending to keep the hard-g sound
# (seguir -> sigo, not siguo); tú/él/ellos keep it since "gu" + e/i is fine.
GUIR_VERBS = {"seguir", "conseguir", "perseguir", "distinguir"}
# 3rd-person-only stem change in the preterite for -ir stem changers above.
PRETERITE_STEM_CHANGE_3RD = {
    "sentir": "i", "preferir": "i", "mentir": "i", "sugerir": "i",
    "dormir": "u", "morir": "u",
    "pedir": "i", "servir": "i", "seguir": "i", "repetir": "i",
    "elegir": "i", "medir": "i",
    "perseguir": "i", "vestir": "i", "despedir": "i", "conseguir": "i",
}

# -cer/-cir verbs (after a vowel) that add a "z" before the "co" ending — only
# the "yo" form is irregular, the rest is regular.
ZC_VERBS = {
    "conocer", "conducir", "producir", "traducir", "nacer", "crecer",
    "parecer", "ofrecer", "agradecer", "merecer", "obedecer", "establecer",
    "reconocer", "pertenecer",
}


REFLEXIVE_PRONOUNS = ["me ", "te ", "se ", "nos ", "os ", "se "]


def strip_reflexive(infinitive: str):
    """Returns (base_infinitive, is_reflexive) — "atreverse" -> ("atrever", True)."""
    if infinitive.endswith("se") and infinitive not in ("ser",):
        return infinitive[:-2], True
    return infinitive, False


def verb_class(infinitive: str) -> str:
    ending = infinitive[-2:]
    return {"ír": "ir"}.get(ending, ending)


def apply_stem_change(stem: str, pattern: str) -> str:
    vowel_from, vowel_to = pattern.split(":")
    idx = stem.rfind(vowel_from)
    if idx == -1:
        return stem
    return stem[:idx] + vowel_to + stem[idx + len(vowel_from):]


def conjugate_present(infinitive: str):
    base, reflexive = strip_reflexive(infinitive)
    if reflexive:
        forms = conjugate_present(base)
        return [pron + form for pron, form in zip(REFLEXIVE_PRONOUNS, forms)]
    if infinitive in IRREGULAR_PRESENT:
        return IRREGULAR_PRESENT[infinitive]

    cls = verb_class(infinitive)
    stem = infinitive[:-2]
    endings = PRESENT_ENDINGS[cls]

    if infinitive in ZC_VERBS:
        forms = [stem + e for e in endings]
        forms[0] = stem[:-1] + "zco"  # conocer -> conozco
        return forms

    if infinitive in STEM_CHANGE_PRESENT:
        pattern = STEM_CHANGE_PRESENT[infinitive]
        changed_stem = apply_stem_change(stem, pattern)
        # nosotros/vosotros (index 3,4) keep the unchanged stem.
        forms = [
            changed_stem + endings[0], changed_stem + endings[1],
            changed_stem + endings[2], stem + endings[3],
            stem + endings[4], changed_stem + endings[5],
        ]
        if infinitive in GUIR_VERBS:
            forms[0] = changed_stem[:-1] + endings[0]  # sigu+o -> sigo (drop u before o)
        return forms

    if infinitive in GUIR_VERBS:
        # -guir verbs with no vowel to stem-change (distinguir) still drop the
        # "u" before an "o" ending: distinguir -> distingo, not distinguo.
        forms = [stem + e for e in endings]
        forms[0] = stem[:-1] + endings[0]
        return forms

    return [stem + e for e in endings]


def conjugate_preterite(infinitive: str):
    base, reflexive = strip_reflexive(infinitive)
    if reflexive:
        forms = conjugate_preterite(base)
        return [pron + form for pron, form in zip(REFLEXIVE_PRONOUNS, forms)]
    if infinitive in IRREGULAR_PRETERITE:
        return IRREGULAR_PRETERITE[infinitive]

    cls = verb_class(infinitive)
    stem = infinitive[:-2]

    if infinitive in PRETERITE_STEM_IRREGULAR:
        irr_stem = PRETERITE_STEM_IRREGULAR[infinitive]
        forms = [irr_stem + e for e in PRETERITE_IRREGULAR_ENDINGS]
        if infinitive == "hacer":
            forms[2] = "hizo"
        return forms

    if infinitive in PRETERITE_J_STEM:
        j_stem = PRETERITE_J_STEM[infinitive]
        return [j_stem + e for e in PRETERITE_J_ENDINGS]

    endings = PRETERITE_ENDINGS[cls]
    forms = [stem + e for e in endings]

    if cls == "ar":
        # Spelling changes that keep the infinitive's consonant sound before
        # the "-é" ending: sacar->saqué, llegar->llegué, cruzar->crucé.
        if stem.endswith("c"):
            forms[0] = stem[:-1] + "qué"
        elif stem.endswith("g"):
            forms[0] = stem + "ué"
        elif stem.endswith("z"):
            forms[0] = stem[:-1] + "cé"

    if infinitive in PRETERITE_STEM_CHANGE_3RD:
        vowel_to = PRETERITE_STEM_CHANGE_3RD[infinitive]
        # Only él/ellos (index 2, 5) change, and only the last stem vowel.
        for i in (2, 5):
            base = stem
            for v in "eo":
                pos = base.rfind(v)
                if pos != -1:
                    forms[i] = base[:pos] + vowel_to + base[pos + 1:] + endings[i]
                    break
    return forms


# ---------------------------------------------------------------------------
# Gendered articles for example sentences
# ---------------------------------------------------------------------------

ARTICLE_OVERRIDE = {
    "agua": "el", "mano": "la", "día": "el", "mapa": "el", "problema": "el",
    "sistema": "el", "programa": "el", "clima": "el", "planeta": "el",
    "poema": "el", "tema": "el", "foto": "la", "moto": "la", "radio": "la",
    "idioma": "el", "arte": "el",
}
FEMININE_SUFFIXES = ("ción", "sión", "dad", "tad", "tud", "umbre", "ie")


def article_for(noun: str) -> str:
    if noun in ARTICLE_OVERRIDE:
        return ARTICLE_OVERRIDE[noun]
    if noun.endswith(FEMININE_SUFFIXES) or noun.endswith("a"):
        return "la"
    return "el"


NOUN_TEMPLATES = [
    "Veo {art} {n} todos los días.",
    "Me gusta {art} {n}.",
    "Necesito {art} {n} para mañana.",
    "{Art} {n} es muy importante.",
    "Aquí está {art} {n}.",
]

VERB_TEMPLATES = [
    "Yo {yo_form} todos los días.",
    "Quiero {inf}.",
    "Voy a {inf} mañana.",
    "No puedo {inf} ahora.",
    "Ella {el_form} cada semana.",
]


def noun_example(noun: str, word_id: int) -> str:
    art = article_for(noun)
    template = NOUN_TEMPLATES[word_id % len(NOUN_TEMPLATES)]
    sentence = template.format(art=art, n=noun, Art=art.capitalize())
    return sentence


def verb_example(infinitive: str, present_forms, word_id: int) -> str:
    if infinitive.endswith("se"):
        # Reflexive verbs read awkwardly with a bare infinitive template
        # ("Quiero atreverse" is wrong) — stick to conjugated-form templates.
        template = ["Yo {yo_form} todos los días.", "Ella {el_form} cada semana."][word_id % 2]
    else:
        template = VERB_TEMPLATES[word_id % len(VERB_TEMPLATES)]
    return template.format(inf=infinitive, yo_form=present_forms[0], el_form=present_forms[2])


# ---------------------------------------------------------------------------
# Word lists: (spanish, english, category)
# A word is skipped if it already appeared earlier in the combined list
# (first occurrence keeps the word; category is assigned by first match).
# ---------------------------------------------------------------------------

VERBS = [
    ("ser", "to be", "general"), ("estar", "to be (state/location)", "general"),
    ("tener", "to have", "general"), ("hacer", "to do / to make", "general"),
    ("poder", "to be able to / can", "general"), ("decir", "to say / to tell", "communication"),
    ("ir", "to go", "travel"), ("ver", "to see", "general"),
    ("dar", "to give", "general"), ("saber", "to know (a fact)", "school"),
    ("querer", "to want / to love", "emotions"), ("llegar", "to arrive", "travel"),
    ("pasar", "to pass / to happen", "general"), ("deber", "to owe / must", "general"),
    ("poner", "to put", "house"), ("parecer", "to seem", "general"),
    ("quedar", "to remain / to stay", "general"), ("creer", "to believe", "general"),
    ("hablar", "to speak", "communication"), ("llevar", "to carry / to wear", "clothing"),
    ("dejar", "to leave / to let", "general"), ("sentir", "to feel", "emotions"),
    ("encontrar", "to find", "general"), ("llamar", "to call", "communication"),
    ("venir", "to come", "travel"), ("pensar", "to think", "general"),
    ("salir", "to leave / to go out", "travel"), ("volver", "to return", "travel"),
    ("tomar", "to take / to drink", "food"), ("conocer", "to know (a person/place)", "general"),
    ("vivir", "to live", "house"), ("escribir", "to write", "school"),
    ("leer", "to read", "school"), ("comer", "to eat", "food"),
    ("beber", "to drink", "food"), ("trabajar", "to work", "work"),
    ("estudiar", "to study", "school"), ("empezar", "to begin", "general"),
    ("terminar", "to finish", "general"), ("jugar", "to play", "sports"),
    ("escuchar", "to listen", "general"), ("entender", "to understand", "school"),
    ("aprender", "to learn", "school"), ("comprar", "to buy", "city"),
    ("buscar", "to look for", "general"), ("necesitar", "to need", "general"),
    ("ayudar", "to help", "general"), ("abrir", "to open", "house"),
    ("cerrar", "to close", "house"), ("andar", "to walk", "travel"),
    ("caer", "to fall", "general"), ("cambiar", "to change", "general"),
    ("cantar", "to sing", "general"), ("celebrar", "to celebrate", "general"),
    ("cocinar", "to cook", "food"), ("comparar", "to compare", "general"),
    ("competir", "to compete", "sports"), ("comprender", "to comprehend", "school"),
    ("conducir", "to drive", "transportation"), ("conseguir", "to get / to achieve", "general"),
    ("construir", "to build", "house"), ("contar", "to count / to tell", "general"),
    ("contestar", "to answer", "communication"), ("continuar", "to continue", "general"),
    ("correr", "to run", "sports"), ("cortar", "to cut", "food"),
    ("crear", "to create", "general"), ("crecer", "to grow", "nature"),
    ("cruzar", "to cross", "city"), ("cuidar", "to take care of", "health"),
    ("cumplir", "to fulfill / to turn (age)", "general"), ("decidir", "to decide", "general"),
    ("dedicar", "to dedicate", "general"), ("defender", "to defend", "general"),
    ("demostrar", "to demonstrate", "general"), ("depender", "to depend", "general"),
    ("descansar", "to rest", "health"), ("descubrir", "to discover", "general"),
    ("desear", "to wish", "emotions"), ("despertar", "to wake up", "general"),
    ("destruir", "to destroy", "general"), ("devolver", "to give back", "general"),
    ("dibujar", "to draw", "school"), ("dirigir", "to direct / to manage", "work"),
    ("disfrutar", "to enjoy", "emotions"), ("dormir", "to sleep", "health"),
    ("dudar", "to doubt", "general"), ("durar", "to last", "time"),
    ("echar", "to throw / to pour", "general"), ("elegir", "to choose", "general"),
    ("empujar", "to push", "general"), ("encantar", "to love (something)", "emotions"),
    ("encender", "to turn on", "technology"), ("enseñar", "to teach", "school"),
    ("entrar", "to enter", "city"), ("entregar", "to deliver / to hand in", "work"),
    ("enviar", "to send", "communication"), ("escapar", "to escape", "general"),
    ("esconder", "to hide", "general"), ("escoger", "to choose", "general"),
    ("esperar", "to wait / to hope", "general"), ("establecer", "to establish", "general"),
    ("evitar", "to avoid", "general"), ("existir", "to exist", "general"),
    ("explicar", "to explain", "school"), ("expresar", "to express", "communication"),
    ("faltar", "to be missing", "general"), ("felicitar", "to congratulate", "communication"),
    ("formar", "to form", "general"), ("funcionar", "to work / to function", "technology"),
    ("ganar", "to win / to earn", "work"), ("gastar", "to spend", "work"),
    ("girar", "to turn", "general"), ("gritar", "to shout", "communication"),
    ("guardar", "to keep / to save", "technology"), ("gustar", "to like", "emotions"),
    ("imaginar", "to imagine", "general"), ("importar", "to matter", "general"),
    ("incluir", "to include", "general"), ("indicar", "to indicate", "general"),
    ("informar", "to inform", "communication"), ("insistir", "to insist", "general"),
    ("intentar", "to try", "general"), ("interesar", "to interest", "emotions"),
    ("invitar", "to invite", "general"), ("juntar", "to gather / to join", "general"),
    ("jurar", "to swear", "general"), ("lanzar", "to throw / to launch", "sports"),
    ("lavar", "to wash", "house"), ("levantar", "to lift / to raise", "health"),
    ("limpiar", "to clean", "house"), ("llenar", "to fill", "general"),
    ("llorar", "to cry", "emotions"), ("lograr", "to achieve", "general"),
    ("luchar", "to fight", "general"), ("mandar", "to send / to order", "communication"),
    ("manejar", "to drive / to manage", "transportation"), ("mantener", "to maintain", "general"),
    ("marcar", "to mark / to dial", "general"), ("matar", "to kill", "general"),
    ("medir", "to measure", "general"), ("mejorar", "to improve", "general"),
    ("mencionar", "to mention", "communication"), ("mentir", "to lie", "communication"),
    ("meter", "to put in", "general"), ("mirar", "to look at", "general"),
    ("molestar", "to bother", "emotions"), ("montar", "to ride / to set up", "sports"),
    ("morir", "to die", "general"), ("mostrar", "to show", "general"),
    ("mover", "to move", "general"), ("nacer", "to be born", "family"),
    ("nadar", "to swim", "sports"), ("negar", "to deny", "general"),
    ("obedecer", "to obey", "general"), ("obligar", "to force", "general"),
    ("observar", "to observe", "general"), ("obtener", "to obtain", "general"),
    ("ocurrir", "to occur", "general"), ("odiar", "to hate", "emotions"),
    ("ofrecer", "to offer", "work"), ("oír", "to hear", "general"),
    ("olvidar", "to forget", "general"), ("opinar", "to think / to opine", "communication"),
    ("organizar", "to organize", "work"), ("pagar", "to pay", "city"),
    ("parar", "to stop", "transportation"), ("participar", "to participate", "general"),
    ("partir", "to leave / to split", "travel"), ("pasear", "to stroll", "city"),
    ("pedir", "to ask for / to order", "food"), ("pegar", "to hit / to stick", "general"),
    ("peinar", "to comb", "health"), ("pelear", "to fight", "general"),
    ("perder", "to lose", "sports"), ("perdonar", "to forgive", "emotions"),
    ("permitir", "to allow", "general"), ("perseguir", "to chase", "general"),
    ("pertenecer", "to belong", "general"), ("pesar", "to weigh", "health"),
    ("pintar", "to paint", "school"), ("planear", "to plan", "travel"),
    ("practicar", "to practice", "sports"), ("preferir", "to prefer", "general"),
    ("preguntar", "to ask", "school"), ("preocupar", "to worry", "emotions"),
    ("preparar", "to prepare", "food"), ("presentar", "to present / to introduce", "work"),
    ("prestar", "to lend", "general"), ("prevenir", "to prevent", "health"),
    ("probar", "to try / to taste", "food"), ("producir", "to produce", "work"),
    ("prometer", "to promise", "general"), ("proteger", "to protect", "general"),
    ("protestar", "to protest", "general"), ("publicar", "to publish", "technology"),
    ("quejar", "to complain", "general"), ("quemar", "to burn", "general"),
    ("quitar", "to remove", "general"), ("recibir", "to receive", "general"),
    ("reconocer", "to recognize", "general"), ("recordar", "to remember", "general"),
    ("reducir", "to reduce", "general"), ("regalar", "to give (a gift)", "general"),
    ("regresar", "to go back", "travel"), ("reír", "to laugh", "emotions"),
    ("relacionar", "to relate", "general"), ("repetir", "to repeat", "school"),
    ("representar", "to represent", "general"), ("resolver", "to solve", "school"),
    ("respetar", "to respect", "general"), ("respirar", "to breathe", "health"),
    ("responder", "to respond", "communication"), ("resultar", "to result", "general"),
    ("reunir", "to gather", "work"), ("robar", "to steal", "general"),
    ("romper", "to break", "general"), ("sacar", "to take out", "general"),
    ("saltar", "to jump", "sports"), ("saludar", "to greet", "communication"),
    ("salvar", "to save (rescue)", "health"), ("secar", "to dry", "house"),
    ("seguir", "to follow / to continue", "general"), ("sembrar", "to plant (seeds)", "nature"),
    ("señalar", "to point out", "general"), ("servir", "to serve", "food"),
    ("significar", "to mean", "general"), ("soltar", "to release", "general"),
    ("sonar", "to sound / to ring", "technology"), ("sonreír", "to smile", "emotions"),
    ("soñar", "to dream", "emotions"), ("sorprender", "to surprise", "emotions"),
    ("subir", "to go up / to upload", "technology"), ("suceder", "to happen", "general"),
    ("sufrir", "to suffer", "health"), ("sugerir", "to suggest", "communication"),
    ("sumar", "to add up", "school"), ("suponer", "to suppose", "general"),
    ("tardar", "to take (time)", "time"), ("temer", "to fear", "emotions"),
    ("tirar", "to throw / to pull", "general"), ("tocar", "to touch / to play (music)", "general"),
    ("traducir", "to translate", "school"), ("traer", "to bring", "general"),
    ("tratar", "to treat / to try", "general"), ("unir", "to unite", "general"),
    ("usar", "to use", "general"), ("utilizar", "to use / to utilize", "general"),
    ("vender", "to sell", "city"), ("viajar", "to travel", "travel"),
    ("visitar", "to visit", "travel"), ("volar", "to fly", "travel"),
    ("votar", "to vote", "general"), ("vestir", "to dress", "clothing"),
    ("despedir", "to say goodbye / to fire", "general"), ("nevar", "to snow", "weather"),
    ("llover", "to rain", "weather"), ("amanecer", "to dawn", "weather"),
    ("anochecer", "to get dark", "weather"), ("bañar", "to bathe", "health"),
    ("afeitar", "to shave", "health"), ("secar", "to dry", "house"),
    # extra verbs to broaden coverage
    ("acabar", "to finish / to run out", "general"), ("aceptar", "to accept", "general"),
    ("acompañar", "to accompany", "general"), ("aconsejar", "to advise", "communication"),
    ("acordar", "to agree / to remember", "general"), ("acostar", "to put to bed", "health"),
    ("actuar", "to act", "general"), ("adivinar", "to guess", "general"),
    ("admirar", "to admire", "emotions"), ("admitir", "to admit", "general"),
    ("adornar", "to decorate", "house"), ("advertir", "to warn", "communication"),
    ("agradecer", "to thank", "communication"), ("alcanzar", "to reach", "general"),
    ("alegrar", "to make happy", "emotions"), ("alquilar", "to rent", "city"),
    ("alzar", "to lift", "general"), ("amar", "to love", "emotions"),
    ("anotar", "to jot down", "school"), ("anunciar", "to announce", "communication"),
    ("apagar", "to turn off", "technology"), ("aparecer", "to appear", "general"),
    ("aplicar", "to apply", "general"), ("apoyar", "to support", "general"),
    ("apreciar", "to appreciate", "emotions"), ("apretar", "to squeeze / to tighten", "general"),
    ("aprobar", "to approve / to pass (an exam)", "school"), ("apuntar", "to point / to write down", "school"),
    ("arreglar", "to fix", "house"), ("arriesgar", "to risk", "general"),
    ("arrojar", "to throw", "general"), ("asegurar", "to assure / to insure", "general"),
    ("asistir", "to attend", "school"), ("asustar", "to scare", "emotions"),
    ("atacar", "to attack", "general"), ("atender", "to attend to", "work"),
    ("atrapar", "to catch", "general"), ("atreverse", "to dare", "emotions"),
    ("aumentar", "to increase", "general"), ("avanzar", "to advance", "general"),
    ("averiguar", "to find out", "general"), ("avisar", "to notify", "communication"),
    ("bailar", "to dance", "sports"), ("bajar", "to go down / to download", "technology"),
    ("besar", "to kiss", "emotions"), ("borrar", "to erase", "technology"),
    ("botar", "to bounce / to throw away", "general"), ("bromear", "to joke", "communication"),
    ("brillar", "to shine", "nature"), ("calcular", "to calculate", "school"),
    ("calentar", "to heat up", "food"), ("callar", "to be quiet", "communication"),
    ("cargar", "to load / to charge", "technology"), ("casar", "to marry", "family"),
    ("castigar", "to punish", "general"), ("charlar", "to chat", "communication"),
    ("chocar", "to crash", "transportation"), ("clasificar", "to classify", "school"),
    ("cobrar", "to charge (money)", "work"), ("coincidir", "to coincide", "general"),
    ("colaborar", "to collaborate", "work"), ("colgar", "to hang", "house"),
    ("colocar", "to place", "house"), ("combinar", "to combine", "general"),
    ("comentar", "to comment", "communication"), ("comprobar", "to verify", "general"),
    ("comunicar", "to communicate", "communication"), ("conectar", "to connect", "technology"),
    ("confesar", "to confess", "communication"), ("confiar", "to trust", "emotions"),
    ("confirmar", "to confirm", "general"), ("congelar", "to freeze", "food"),
    ("conquistar", "to conquer", "general"), ("consistir", "to consist of", "general"),
    ("consultar", "to consult", "work"), ("consumir", "to consume", "general"),
    ("contactar", "to contact", "communication"), ("contaminar", "to pollute", "nature"),
    ("contener", "to contain", "general"), ("contribuir", "to contribute", "general"),
    ("controlar", "to control", "general"), ("convencer", "to convince", "communication"),
    ("convertir", "to convert", "general"), ("copiar", "to copy", "school"),
    ("coser", "to sew", "clothing"), ("criar", "to raise (children)", "family"),
    ("criticar", "to criticize", "communication"), ("cultivar", "to cultivate", "nature"),
    ("curar", "to cure", "health"), ("dañar", "to damage", "general"),
    ("debatir", "to debate", "communication"), ("declarar", "to declare", "communication"),
    ("dedicarse", "to dedicate oneself", "work"), ("desaparecer", "to disappear", "general"),
    ("desarrollar", "to develop", "work"), ("descargar", "to download", "technology"),
    ("descubrir", "to discover", "general"), ("desperdiciar", "to waste", "general"),
    ("diseñar", "to design", "work"), ("disminuir", "to decrease", "general"),
    ("disparar", "to shoot", "general"), ("distinguir", "to distinguish", "general"),
    ("distribuir", "to distribute", "work"), ("divertir", "to have fun", "emotions"),
    ("dividir", "to divide", "school"), ("doblar", "to fold / to turn", "general"),
    ("editar", "to edit", "technology"), ("educar", "to educate", "school"),
    ("ejercer", "to practice (a profession)", "work"), ("embarcar", "to board", "travel"),
    ("emigrar", "to emigrate", "travel"), ("emocionar", "to excite", "emotions"),
    ("empatar", "to tie (a game)", "sports"), ("emplear", "to employ / to use", "work"),
    ("encajar", "to fit", "general"), ("encargar", "to order / to put in charge", "work"),
    ("encerrar", "to lock up", "general"), ("enfadar", "to anger", "emotions"),
    ("enfermar", "to get sick", "health"), ("enfrentar", "to face", "general"),
    ("engañar", "to deceive", "general"), ("enojar", "to anger", "emotions"),
    ("ensuciar", "to make dirty", "house"), ("enterar", "to find out", "general"),
    ("entrenar", "to train", "sports"), ("entrevistar", "to interview", "work"),
    ("equivocar", "to make a mistake", "general"), ("escalar", "to climb", "sports"),
    ("estrenar", "to premiere / to use for the first time", "general"),
    ("evaluar", "to evaluate", "school"), ("exigir", "to demand", "general"),
    ("existir", "to exist", "general"), ("experimentar", "to experience", "general"),
    ("exportar", "to export", "work"), ("extrañar", "to miss (someone)", "emotions"),
    ("fabricar", "to manufacture", "work"), ("facilitar", "to facilitate", "general"),
    ("festejar", "to celebrate", "general"), ("fijar", "to fix / to set", "general"),
    ("financiar", "to finance", "work"), ("firmar", "to sign", "work"),
    ("fracasar", "to fail", "general"), ("frenar", "to brake", "transportation"),
    ("gozar", "to enjoy", "emotions"), ("grabar", "to record", "technology"),
    ("guiar", "to guide", "travel"), ("hallar", "to find", "general"),
    ("herir", "to injure", "health"), ("hervir", "to boil", "food"),
    ("identificar", "to identify", "general"), ("igualar", "to equalize", "general"),
    ("importar", "to import / to matter", "work"), ("impresionar", "to impress", "emotions"),
    ("imprimir", "to print", "technology"), ("inaugurar", "to inaugurate", "general"),
    ("inspirar", "to inspire", "emotions"), ("instalar", "to install", "technology"),
    ("integrar", "to integrate", "general"), ("interrumpir", "to interrupt", "communication"),
    ("investigar", "to investigate", "school"), ("invertir", "to invest", "work"),
    ("involucrar", "to involve", "general"), ("justificar", "to justify", "general"),
    ("limitar", "to limit", "general"), ("localizar", "to locate", "general"),
    ("madurar", "to mature", "general"), ("maltratar", "to mistreat", "general"),
    ("manifestar", "to demonstrate / to express", "communication"), ("marchar", "to march / to leave", "travel"),
    ("masticar", "to chew", "food"), ("memorizar", "to memorize", "school"),
    ("merecer", "to deserve", "general"), ("mezclar", "to mix", "food"),
    ("modificar", "to modify", "general"), ("molestarse", "to get annoyed", "emotions"),
    ("multiplicar", "to multiply", "school"), ("navegar", "to sail / to browse", "technology"),
    ("negociar", "to negotiate", "work"), ("notar", "to notice", "general"),
    ("notificar", "to notify", "communication"), ("nutrir", "to nourish", "health"),
    ("odiar", "to hate", "emotions"), ("opinar", "to give an opinion", "communication"),
    ("orar", "to pray", "general"), ("ordenar", "to order / to tidy up", "house"),
    ("organizar", "to organize", "work"), ("pactar", "to agree on", "general"),
    ("padecer", "to suffer from", "health"), ("palpar", "to touch / to feel", "body"),
    ("parpadear", "to blink", "body"), ("patinar", "to skate", "sports"),
    ("pescar", "to fish", "sports"), ("planchar", "to iron", "house"),
    ("plantar", "to plant", "nature"), ("poblar", "to populate", "general"),
    ("presenciar", "to witness", "general"), ("presumir", "to boast", "general"),
    ("prevenir", "to prevent", "health"), ("procesar", "to process", "technology"),
    ("proclamar", "to proclaim", "general"), ("programar", "to program", "technology"),
    ("prohibir", "to prohibit", "general"), ("prolongar", "to prolong", "general"),
    ("promover", "to promote", "work"), ("pronunciar", "to pronounce", "school"),
    ("proponer", "to propose", "general"), ("provocar", "to provoke", "general"),
    ("publicar", "to publish", "technology"), ("rascar", "to scratch", "body"),
    ("realizar", "to carry out", "general"), ("rebajar", "to lower (price)", "city"),
    ("recargar", "to recharge", "technology"), ("rechazar", "to reject", "general"),
    ("recoger", "to pick up", "house"), ("recomendar", "to recommend", "general"),
    ("reconstruir", "to rebuild", "house"), ("recorrer", "to travel through", "travel"),
    ("recuperar", "to recover", "health"), ("reflejar", "to reflect", "general"),
    ("reformar", "to reform / to renovate", "house"), ("regar", "to water (plants)", "nature"),
    ("registrar", "to register", "work"), ("regular", "to regulate", "general"),
    ("rellenar", "to fill in", "school"), ("remover", "to remove / to stir", "general"),
    ("renovar", "to renew", "general"), ("rentar", "to rent", "city"),
    ("reparar", "to repair", "house"), ("repasar", "to review", "school"),
    ("reservar", "to reserve", "travel"), ("resistir", "to resist", "general"),
    ("restaurar", "to restore", "general"), ("resumir", "to summarize", "school"),
    ("retirar", "to withdraw", "general"), ("revisar", "to review / to check", "work"),
    ("revolver", "to stir / to mix", "food"), ("rodear", "to surround", "general"),
    ("rozar", "to graze / to touch lightly", "body"), ("saborear", "to savor", "food"),
    ("satisfacer", "to satisfy", "general"), ("secuestrar", "to kidnap", "general"),
    ("seleccionar", "to select", "general"), ("separar", "to separate", "general"),
    ("simplificar", "to simplify", "general"), ("situar", "to place / to locate", "general"),
    ("solicitar", "to request", "work"), ("solucionar", "to solve", "general"),
    ("sospechar", "to suspect", "general"), ("sostener", "to hold / to support", "general"),
    ("suavizar", "to soften", "general"), ("subrayar", "to underline", "school"),
    ("substituir", "to substitute", "general"), ("sumergir", "to submerge", "nature"),
    ("superar", "to overcome", "general"), ("suspender", "to fail (an exam) / to suspend", "school"),
    ("sustituir", "to substitute", "general"), ("tapar", "to cover", "house"),
    ("tejer", "to knit / to weave", "clothing"), ("teñir", "to dye", "clothing"),
    ("titular", "to title / to headline", "communication"), ("tocar", "to touch", "body"),
    ("tolerar", "to tolerate", "general"), ("torcer", "to twist", "body"),
    ("trasladar", "to move / to relocate", "work"), ("triunfar", "to succeed", "general"),
    ("tropezar", "to trip", "body"), ("unificar", "to unify", "general"),
    ("vaciar", "to empty", "house"), ("vagar", "to wander", "general"),
    ("valorar", "to value", "general"), ("variar", "to vary", "general"),
    ("vencer", "to defeat / to expire", "sports"), ("vengar", "to avenge", "general"),
    ("verificar", "to verify", "general"), ("vigilar", "to watch over", "general"),
    ("vincular", "to link", "general"), ("violar", "to violate", "general"),
]

NOUNS = [
    # house
    ("casa", "house", "house"), ("habitación", "room", "house"), ("cocina", "kitchen", "house"),
    ("baño", "bathroom", "house"), ("dormitorio", "bedroom", "house"), ("sala", "living room", "house"),
    ("jardín", "garden", "house"), ("puerta", "door", "house"), ("ventana", "window", "house"),
    ("techo", "roof / ceiling", "house"), ("pared", "wall", "house"), ("suelo", "floor", "house"),
    ("mesa", "table", "house"), ("silla", "chair", "house"), ("cama", "bed", "house"),
    ("sofá", "sofa", "house"), ("armario", "closet", "house"), ("estante", "shelf", "house"),
    ("lámpara", "lamp", "house"), ("espejo", "mirror", "house"), ("cortina", "curtain", "house"),
    ("alfombra", "rug", "house"), ("escalera", "stairs", "house"), ("balcón", "balcony", "house"),
    ("garaje", "garage", "house"), ("patio", "patio / yard", "house"), ("chimenea", "fireplace", "house"),
    ("llave", "key", "house"), ("cerradura", "lock", "house"), ("timbre", "doorbell", "house"),
    ("nevera", "fridge", "house"), ("horno", "oven", "house"), ("lavadora", "washing machine", "house"),
    ("microondas", "microwave", "house"), ("aspiradora", "vacuum cleaner", "house"),
    ("plancha", "iron", "house"), ("sartén", "frying pan", "house"), ("olla", "pot", "house"),
    ("plato", "plate", "house"), ("vaso", "glass", "house"), ("cuchara", "spoon", "house"),
    ("tenedor", "fork", "house"), ("cuchillo", "knife", "house"), ("toalla", "towel", "house"),
    ("almohada", "pillow", "house"), ("manta", "blanket", "house"), ("sábana", "bed sheet", "house"),
    ("jabón", "soap", "house"), ("basura", "trash", "house"), ("techo", "ceiling", "house"),
    # nature
    ("naturaleza", "nature", "nature"), ("árbol", "tree", "nature"), ("flor", "flower", "nature"),
    ("planta", "plant", "nature"), ("hoja", "leaf", "nature"), ("bosque", "forest", "nature"),
    ("montaña", "mountain", "nature"), ("río", "river", "nature"), ("lago", "lake", "nature"),
    ("mar", "sea", "nature"), ("océano", "ocean", "nature"), ("playa", "beach", "nature"),
    ("arena", "sand", "nature"), ("piedra", "stone", "nature"), ("roca", "rock", "nature"),
    ("cielo", "sky", "nature"), ("sol", "sun", "nature"), ("luna", "moon", "nature"),
    ("estrella", "star", "nature"), ("nube", "cloud", "nature"), ("tierra", "earth / land", "nature"),
    ("campo", "countryside / field", "nature"), ("valle", "valley", "nature"), ("colina", "hill", "nature"),
    ("isla", "island", "nature"), ("desierto", "desert", "nature"), ("selva", "jungle", "nature"),
    ("hierba", "grass", "nature"), ("raíz", "root", "nature"), ("semilla", "seed", "nature"),
    ("rama", "branch", "nature"), ("nido", "nest", "nature"), ("cueva", "cave", "nature"),
    ("volcán", "volcano", "nature"), ("cascada", "waterfall", "nature"),
    # animals
    ("animal", "animal", "animals"), ("perro", "dog", "animals"), ("gato", "cat", "animals"),
    ("caballo", "horse", "animals"), ("vaca", "cow", "animals"), ("cerdo", "pig", "animals"),
    ("oveja", "sheep", "animals"), ("gallina", "hen", "animals"), ("pájaro", "bird", "animals"),
    ("pez", "fish", "animals"), ("león", "lion", "animals"), ("tigre", "tiger", "animals"),
    ("elefante", "elephant", "animals"), ("mono", "monkey", "animals"), ("oso", "bear", "animals"),
    ("lobo", "wolf", "animals"), ("zorro", "fox", "animals"), ("conejo", "rabbit", "animals"),
    ("ratón", "mouse", "animals"), ("serpiente", "snake", "animals"), ("tortuga", "turtle", "animals"),
    ("rana", "frog", "animals"), ("insecto", "insect", "animals"), ("mosca", "fly", "animals"),
    ("abeja", "bee", "animals"), ("araña", "spider", "animals"), ("mariposa", "butterfly", "animals"),
    ("águila", "eagle", "animals"), ("tiburón", "shark", "animals"), ("ballena", "whale", "animals"),
    ("delfín", "dolphin", "animals"), ("cocodrilo", "crocodile", "animals"), ("jirafa", "giraffe", "animals"),
    ("cebra", "zebra", "animals"),
    # city
    ("ciudad", "city", "city"), ("calle", "street", "city"), ("avenida", "avenue", "city"),
    ("plaza", "square", "city"), ("edificio", "building", "city"), ("tienda", "store", "city"),
    ("mercado", "market", "city"), ("banco", "bank", "city"), ("hospital", "hospital", "city"),
    ("farmacia", "pharmacy", "city"), ("restaurante", "restaurant", "city"), ("hotel", "hotel", "city"),
    ("museo", "museum", "city"), ("biblioteca", "library", "city"), ("iglesia", "church", "city"),
    ("parque", "park", "city"), ("estadio", "stadium", "city"), ("aeropuerto", "airport", "city"),
    ("estación", "station", "city"), ("semáforo", "traffic light", "city"), ("acera", "sidewalk", "city"),
    ("esquina", "corner", "city"), ("barrio", "neighborhood", "city"), ("ayuntamiento", "city hall", "city"),
    ("policía", "police", "city"), ("bombero", "firefighter", "city"), ("oficina", "office", "city"),
    ("fábrica", "factory", "city"), ("supermercado", "supermarket", "city"), ("cine", "cinema", "city"),
    ("teatro", "theater", "city"), ("gimnasio", "gym", "city"), ("universidad", "university", "city"),
    # travel
    ("viaje", "trip", "travel"), ("vacaciones", "vacation", "travel"), ("maleta", "suitcase", "travel"),
    ("pasaporte", "passport", "travel"), ("billete", "ticket", "travel"), ("boleto", "ticket", "travel"),
    ("turista", "tourist", "travel"), ("mapa", "map", "travel"), ("itinerario", "itinerary", "travel"),
    ("aventura", "adventure", "travel"), ("destino", "destination", "travel"), ("excursión", "excursion", "travel"),
    ("frontera", "border", "travel"), ("guía", "guide", "travel"), ("reserva", "reservation", "travel"),
    ("equipaje", "luggage", "travel"), ("crucero", "cruise", "travel"), ("campamento", "campsite", "travel"),
    ("brújula", "compass", "travel"),
    # transportation
    ("coche", "car", "transportation"), ("carro", "car", "transportation"), ("autobús", "bus", "transportation"),
    ("tren", "train", "transportation"), ("avión", "airplane", "transportation"), ("barco", "boat", "transportation"),
    ("bicicleta", "bicycle", "transportation"), ("motocicleta", "motorcycle", "transportation"),
    ("taxi", "taxi", "transportation"), ("metro", "subway", "transportation"), ("camión", "truck", "transportation"),
    ("helicóptero", "helicopter", "transportation"), ("carretera", "highway", "transportation"),
    ("autopista", "freeway", "transportation"), ("rueda", "wheel", "transportation"), ("motor", "engine", "transportation"),
    # food
    ("comida", "food", "food"), ("desayuno", "breakfast", "food"), ("almuerzo", "lunch", "food"),
    ("cena", "dinner", "food"), ("pan", "bread", "food"), ("leche", "milk", "food"),
    ("queso", "cheese", "food"), ("huevo", "egg", "food"), ("carne", "meat", "food"),
    ("pollo", "chicken", "food"), ("pescado", "fish (food)", "food"), ("arroz", "rice", "food"),
    ("pasta", "pasta", "food"), ("sopa", "soup", "food"), ("ensalada", "salad", "food"),
    ("verdura", "vegetable", "food"), ("fruta", "fruit", "food"), ("manzana", "apple", "food"),
    ("plátano", "banana", "food"), ("naranja", "orange", "food"), ("uva", "grape", "food"),
    ("fresa", "strawberry", "food"), ("limón", "lemon", "food"), ("tomate", "tomato", "food"),
    ("patata", "potato", "food"), ("cebolla", "onion", "food"), ("ajo", "garlic", "food"),
    ("zanahoria", "carrot", "food"), ("lechuga", "lettuce", "food"), ("azúcar", "sugar", "food"),
    ("sal", "salt", "food"), ("pimienta", "pepper", "food"), ("aceite", "oil", "food"),
    ("mantequilla", "butter", "food"), ("mermelada", "jam", "food"), ("chocolate", "chocolate", "food"),
    ("café", "coffee", "food"), ("té", "tea", "food"), ("agua", "water", "food"),
    ("jugo", "juice", "food"), ("vino", "wine", "food"), ("cerveza", "beer", "food"),
    ("postre", "dessert", "food"), ("pastel", "cake", "food"), ("galleta", "cookie", "food"),
    ("helado", "ice cream", "food"), ("sándwich", "sandwich", "food"), ("hamburguesa", "hamburger", "food"),
    ("pizza", "pizza", "food"), ("tortilla", "omelette / tortilla", "food"), ("miel", "honey", "food"),
    ("harina", "flour", "food"), ("cereal", "cereal", "food"),
    # family
    ("familia", "family", "family"), ("madre", "mother", "family"), ("padre", "father", "family"),
    ("hijo", "son", "family"), ("hija", "daughter", "family"), ("hermano", "brother", "family"),
    ("hermana", "sister", "family"), ("abuelo", "grandfather", "family"), ("abuela", "grandmother", "family"),
    ("tío", "uncle", "family"), ("tía", "aunt", "family"), ("primo", "cousin (m)", "family"),
    ("prima", "cousin (f)", "family"), ("sobrino", "nephew", "family"), ("sobrina", "niece", "family"),
    ("esposo", "husband", "family"), ("esposa", "wife", "family"), ("novio", "boyfriend", "family"),
    ("novia", "girlfriend", "family"), ("nieto", "grandson", "family"), ("nieta", "granddaughter", "family"),
    ("suegro", "father-in-law", "family"), ("suegra", "mother-in-law", "family"),
    ("cuñado", "brother-in-law", "family"), ("cuñada", "sister-in-law", "family"),
    ("bebé", "baby", "family"), ("pareja", "partner / couple", "family"),
    # body
    ("cuerpo", "body", "body"), ("cabeza", "head", "body"), ("cara", "face", "body"),
    ("ojo", "eye", "body"), ("nariz", "nose", "body"), ("boca", "mouth", "body"),
    ("oreja", "ear", "body"), ("diente", "tooth", "body"), ("pelo", "hair", "body"),
    ("cuello", "neck", "body"), ("hombro", "shoulder", "body"), ("brazo", "arm", "body"),
    ("mano", "hand", "body"), ("dedo", "finger", "body"), ("pecho", "chest", "body"),
    ("espalda", "back", "body"), ("estómago", "stomach", "body"), ("pierna", "leg", "body"),
    ("rodilla", "knee", "body"), ("pie", "foot", "body"), ("corazón", "heart", "body"),
    ("cerebro", "brain", "body"), ("piel", "skin", "body"), ("uña", "nail", "body"),
    ("ceja", "eyebrow", "body"), ("labio", "lip", "body"), ("lengua", "tongue", "body"),
    ("hueso", "bone", "body"), ("sangre", "blood", "body"), ("músculo", "muscle", "body"),
    # health
    ("salud", "health", "health"), ("enfermedad", "illness", "health"), ("dolor", "pain", "health"),
    ("fiebre", "fever", "health"), ("medicina", "medicine", "health"), ("doctor", "doctor", "health"),
    ("médico", "doctor", "health"), ("enfermera", "nurse", "health"), ("receta", "prescription", "health"),
    ("pastilla", "pill", "health"), ("vacuna", "vaccine", "health"), ("herida", "wound", "health"),
    ("gripe", "flu", "health"), ("tos", "cough", "health"), ("alergia", "allergy", "health"),
    ("síntoma", "symptom", "health"), ("tratamiento", "treatment", "health"), ("cirugía", "surgery", "health"),
    ("ambulancia", "ambulance", "health"),
    # clothing
    ("ropa", "clothes", "clothing"), ("camisa", "shirt", "clothing"), ("pantalón", "pants", "clothing"),
    ("vestido", "dress", "clothing"), ("falda", "skirt", "clothing"), ("zapato", "shoe", "clothing"),
    ("calcetín", "sock", "clothing"), ("chaqueta", "jacket", "clothing"), ("abrigo", "coat", "clothing"),
    ("sombrero", "hat", "clothing"), ("gorra", "cap", "clothing"), ("guante", "glove", "clothing"),
    ("bufanda", "scarf", "clothing"), ("cinturón", "belt", "clothing"), ("corbata", "tie", "clothing"),
    ("traje", "suit", "clothing"), ("pijama", "pajamas", "clothing"), ("bota", "boot", "clothing"),
    ("sandalia", "sandal", "clothing"), ("bolsillo", "pocket", "clothing"), ("botón", "button", "clothing"),
    ("tela", "fabric", "clothing"), ("moda", "fashion", "clothing"), ("uniforme", "uniform", "clothing"),
    # work
    ("trabajo", "work / job", "work"), ("jefe", "boss", "work"), ("empleado", "employee", "work"),
    ("empresa", "company", "work"), ("reunión", "meeting", "work"), ("proyecto", "project", "work"),
    ("salario", "salary", "work"), ("sueldo", "salary", "work"), ("contrato", "contract", "work"),
    ("entrevista", "interview", "work"), ("colega", "colleague", "work"), ("negocio", "business", "work"),
    ("cliente", "client", "work"), ("producto", "product", "work"), ("servicio", "service", "work"),
    ("factura", "invoice", "work"), ("impuesto", "tax", "work"), ("horario", "schedule", "work"),
    ("carrera", "career", "work"), ("profesión", "profession", "work"), ("informe", "report", "work"),
    # school
    ("escuela", "school", "school"), ("maestro", "teacher (m)", "school"), ("profesor", "teacher / professor", "school"),
    ("estudiante", "student", "school"), ("alumno", "pupil", "school"), ("clase", "class", "school"),
    ("examen", "exam", "school"), ("tarea", "homework", "school"), ("libro", "book", "school"),
    ("cuaderno", "notebook", "school"), ("lápiz", "pencil", "school"), ("bolígrafo", "pen", "school"),
    ("pizarra", "chalkboard", "school"), ("mochila", "backpack", "school"), ("nota", "grade / note", "school"),
    ("curso", "course", "school"), ("lección", "lesson", "school"), ("materia", "subject", "school"),
    ("matemáticas", "mathematics", "school"), ("historia", "history", "school"), ("ciencia", "science", "school"),
    ("idioma", "language", "school"),
    # time
    ("tiempo", "time / weather", "time"), ("hora", "hour", "time"), ("minuto", "minute", "time"),
    ("segundo", "second", "time"), ("día", "day", "time"), ("semana", "week", "time"),
    ("mes", "month", "time"), ("año", "year", "time"), ("mañana", "morning / tomorrow", "time"),
    ("tarde", "afternoon", "time"), ("noche", "night", "time"), ("momento", "moment", "time"),
    ("fecha", "date", "time"), ("calendario", "calendar", "time"), ("reloj", "clock", "time"),
    ("siglo", "century", "time"), ("época", "era", "time"), ("plazo", "deadline", "time"),
    ("temporada", "season (of time)", "time"),
    # weather
    ("clima", "climate", "weather"), ("nieve", "snow", "weather"), ("tormenta", "storm", "weather"),
    ("huracán", "hurricane", "weather"), ("niebla", "fog", "weather"), ("humedad", "humidity", "weather"),
    ("temperatura", "temperature", "weather"), ("calor", "heat", "weather"), ("frío", "cold", "weather"),
    ("viento", "wind", "weather"), ("granizo", "hail", "weather"), ("trueno", "thunder", "weather"),
    ("relámpago", "lightning", "weather"), ("lluvia", "rain", "weather"), ("arcoíris", "rainbow", "weather"),
    # technology
    ("computadora", "computer", "technology"), ("ordenador", "computer", "technology"),
    ("teléfono", "telephone", "technology"), ("internet", "internet", "technology"),
    ("correo", "mail / email", "technology"), ("aplicación", "application", "technology"),
    ("programa", "program", "technology"), ("pantalla", "screen", "technology"),
    ("teclado", "keyboard", "technology"), ("impresora", "printer", "technology"),
    ("cámara", "camera", "technology"), ("batería", "battery", "technology"),
    ("cargador", "charger", "technology"), ("contraseña", "password", "technology"),
    ("archivo", "file", "technology"), ("dato", "data", "technology"),
    ("red", "network", "technology"), ("dispositivo", "device", "technology"),
    # sports
    ("deporte", "sport", "sports"), ("fútbol", "soccer", "sports"), ("baloncesto", "basketball", "sports"),
    ("tenis", "tennis", "sports"), ("natación", "swimming", "sports"), ("equipo", "team", "sports"),
    ("jugador", "player", "sports"), ("partido", "match", "sports"), ("gol", "goal", "sports"),
    ("pelota", "ball", "sports"), ("cancha", "court / field", "sports"), ("entrenador", "coach", "sports"),
    ("campeón", "champion", "sports"), ("medalla", "medal", "sports"), ("competencia", "competition", "sports"),
    ("maratón", "marathon", "sports"), ("ciclismo", "cycling", "sports"), ("gimnasia", "gymnastics", "sports"),
    ("boxeo", "boxing", "sports"),
    # emotions
    ("amor", "love", "emotions"), ("alegría", "joy", "emotions"), ("tristeza", "sadness", "emotions"),
    ("miedo", "fear", "emotions"), ("ira", "anger", "emotions"), ("sorpresa", "surprise", "emotions"),
    ("felicidad", "happiness", "emotions"), ("esperanza", "hope", "emotions"), ("orgullo", "pride", "emotions"),
    ("vergüenza", "shame", "emotions"), ("envidia", "envy", "emotions"), ("celos", "jealousy", "emotions"),
    ("calma", "calm", "emotions"), ("ansiedad", "anxiety", "emotions"), ("pasión", "passion", "emotions"),
    ("odio", "hate", "emotions"), ("nostalgia", "nostalgia", "emotions"), ("entusiasmo", "enthusiasm", "emotions"),
    # colors
    ("color", "color", "colors"), ("rojo", "red", "colors"), ("azul", "blue", "colors"),
    ("verde", "green", "colors"), ("amarillo", "yellow", "colors"), ("negro", "black", "colors"),
    ("blanco", "white", "colors"), ("gris", "gray", "colors"), ("rosa", "pink", "colors"),
    ("morado", "purple", "colors"), ("marrón", "brown", "colors"),
    # general (catch-all everyday nouns)
    ("persona", "person", "general"), ("gente", "people", "general"), ("lugar", "place", "general"),
    ("cosa", "thing", "general"), ("idea", "idea", "general"), ("problema", "problem", "general"),
    ("solución", "solution", "general"), ("pregunta", "question", "general"), ("respuesta", "answer", "general"),
    ("noticia", "news", "general"), ("información", "information", "general"), ("ejemplo", "example", "general"),
    ("razón", "reason", "general"), ("manera", "way / manner", "general"), ("forma", "shape / form", "general"),
    ("parte", "part", "general"), ("grupo", "group", "general"), ("número", "number", "general"),
    ("lista", "list", "general"), ("nombre", "name", "general"), ("palabra", "word", "general"),
    ("letra", "letter", "general"), ("frase", "sentence / phrase", "general"), ("página", "page", "general"),
    ("papel", "paper", "general"), ("caja", "box", "general"), ("bolsa", "bag", "general"),
    ("regalo", "gift", "general"), ("fiesta", "party", "general"), ("música", "music", "general"),
    ("canción", "song", "general"), ("arte", "art", "general"), ("pintura", "painting", "general"),
    ("foto", "photo", "general"), ("video", "video", "general"), ("juego", "game", "general"),
    ("juguete", "toy", "general"), ("dinero", "money", "general"), ("moneda", "coin / currency", "general"),
    ("tarjeta", "card", "general"), ("precio", "price", "general"), ("descuento", "discount", "general"),
    ("mundo", "world", "general"), ("país", "country", "general"), ("vida", "life", "general"),
    ("amigo", "friend", "general"), ("hombre", "man", "general"), ("mujer", "woman", "general"),
    ("niño", "boy / child", "general"), ("niña", "girl", "general"), ("adulto", "adult", "general"),
    ("público", "public / audience", "general"), ("gobierno", "government", "general"),
    ("ley", "law", "general"), ("guerra", "war", "general"), ("paz", "peace", "general"),
    ("religión", "religion", "general"), ("cultura", "culture", "general"), ("historia", "history / story", "general"),
    # extra nouns to broaden coverage
    ("estufa", "stove", "house"), ("grifo", "faucet", "house"), ("enchufe", "electrical outlet", "house"),
    ("cajón", "drawer", "house"), ("cerca", "fence", "house"), ("tejado", "rooftop", "house"),
    ("ático", "attic", "house"), ("sótano", "basement", "house"), ("pasillo", "hallway", "house"),
    ("cortinilla", "blind", "house"), ("maceta", "flower pot", "house"), ("candado", "padlock", "house"),
    ("bombilla", "light bulb", "house"), ("interruptor", "light switch", "house"), ("escoba", "broom", "house"),
    ("trapo", "rag", "house"), ("cubo", "bucket", "house"), ("tijeras", "scissors", "house"),
    ("rocío", "dew", "nature"), ("relieve", "terrain", "nature"), ("costa", "coast", "nature"),
    ("acantilado", "cliff", "nature"), ("pantano", "swamp", "nature"), ("glaciar", "glacier", "nature"),
    ("cordillera", "mountain range", "nature"), ("manantial", "spring (water)", "nature"),
    ("arbusto", "bush", "nature"), ("tronco", "trunk (tree)", "nature"), ("corteza", "bark / crust", "nature"),
    ("polvo", "dust", "nature"), ("barro", "mud", "nature"), ("escarcha", "frost", "nature"),
    ("oveja negra", "black sheep", "animals"), ("cordero", "lamb", "animals"), ("pato", "duck", "animals"),
    ("ganso", "goose", "animals"), ("pavo", "turkey", "animals"), ("burro", "donkey", "animals"),
    ("cabra", "goat", "animals"), ("hormiga", "ant", "animals"), ("escarabajo", "beetle", "animals"),
    ("saltamontes", "grasshopper", "animals"), ("caracol", "snail", "animals"), ("cangrejo", "crab", "animals"),
    ("camarón", "shrimp", "animals"), ("pulpo", "octopus", "animals"), ("foca", "seal", "animals"),
    ("murciélago", "bat", "animals"), ("ardilla", "squirrel", "animals"), ("búho", "owl", "animals"),
    ("pingüino", "penguin", "animals"), ("canguro", "kangaroo", "animals"),
    ("rotonda", "roundabout", "city"), ("puente", "bridge", "city"), ("túnel", "tunnel", "city"),
    ("estacionamiento", "parking lot", "city"), ("alcantarilla", "sewer", "city"), ("farola", "streetlight", "city"),
    ("kiosco", "kiosk", "city"), ("peluquería", "hair salon", "city"), ("panadería", "bakery", "city"),
    ("carnicería", "butcher shop", "city"), ("librería", "bookstore", "city"), ("juguetería", "toy store", "city"),
    ("zapatería", "shoe store", "city"), ("lavandería", "laundromat", "city"), ("gasolinera", "gas station", "city"),
    ("plaza mayor", "main square", "city"), ("acueducto", "aqueduct", "city"), ("monumento", "monument", "city"),
    ("torre", "tower", "city"), ("catedral", "cathedral", "city"),
    ("mochilero", "backpacker", "travel"), ("visado", "visa", "travel"), ("aduana", "customs", "travel"),
    ("embajada", "embassy", "travel"), ("hostal", "hostel", "travel"), ("recepción", "reception desk", "travel"),
    ("propina", "tip (gratuity)", "travel"), ("divisa", "foreign currency", "travel"),
    ("souvenir", "souvenir", "travel"), ("postal", "postcard", "travel"),
    ("bote salvavidas", "lifeboat", "transportation"), ("velero", "sailboat", "transportation"),
    ("furgoneta", "van", "transportation"), ("cohete", "rocket", "transportation"),
    ("tranvía", "tram", "transportation"), ("patineta", "skateboard", "transportation"),
    ("monopatín", "scooter", "transportation"), ("neumático", "tire", "transportation"),
    ("volante", "steering wheel", "transportation"), ("freno", "brake", "transportation"),
    ("almendra", "almond", "food"), ("nuez", "walnut", "food"), ("maíz", "corn", "food"),
    ("espinaca", "spinach", "food"), ("pepino", "cucumber", "food"), ("pimiento", "bell pepper", "food"),
    ("champiñón", "mushroom", "food"), ("aguacate", "avocado", "food"), ("piña", "pineapple", "food"),
    ("sandía", "watermelon", "food"), ("melón", "melon", "food"), ("cereza", "cherry", "food"),
    ("durazno", "peach", "food"), ("pera", "pear", "food"), ("coco", "coconut", "food"),
    ("yogur", "yogurt", "food"), ("mostaza", "mustard", "food"), ("vinagre", "vinegar", "food"),
    ("caldo", "broth", "food"), ("guiso", "stew", "food"), ("bocadillo", "sandwich (snack)", "food"),
    ("aperitivo", "appetizer", "food"), ("condimento", "condiment", "food"), ("especia", "spice", "food"),
    ("bandeja", "tray", "food"), ("servilleta", "napkin", "food"), ("mantel", "tablecloth", "food"),
    ("madrastra", "stepmother", "family"), ("padrastro", "stepfather", "family"), ("hermanastro", "stepbrother", "family"),
    ("gemelo", "twin", "family"), ("padrino", "godfather", "family"), ("madrina", "godmother", "family"),
    ("ahijado", "godson", "family"), ("antepasado", "ancestor", "family"), ("descendiente", "descendant", "family"),
    ("viudo", "widower", "family"), ("soltero", "single (person)", "family"),
    ("codo", "elbow", "body"), ("muñeca", "wrist", "body"), ("tobillo", "ankle", "body"),
    ("cintura", "waist", "body"), ("cadera", "hip", "body"), ("nuca", "nape of the neck", "body"),
    ("frente", "forehead", "body"), ("mejilla", "cheek", "body"), ("barbilla", "chin", "body"),
    ("pestaña", "eyelash", "body"), ("pupila", "pupil (eye)", "body"), ("costilla", "rib", "body"),
    ("pulmón", "lung", "body"), ("riñón", "kidney", "body"), ("hígado", "liver", "body"),
    ("intestino", "intestine", "body"), ("vena", "vein", "body"), ("nervio", "nerve", "body"),
    ("cicatriz", "scar", "health"), ("moretón", "bruise", "health"), ("quemadura", "burn", "health"),
    ("infección", "infection", "health"), ("inyección", "injection", "health"), ("jarabe", "syrup (medicine)", "health"),
    ("venda", "bandage", "health"), ("muleta", "crutch", "health"), ("silla de ruedas", "wheelchair", "health"),
    ("terapia", "therapy", "health"),
    ("blusa", "blouse", "clothing"), ("chaleco", "vest", "clothing"), ("short", "shorts", "clothing"),
    ("overol", "overalls", "clothing"), ("camiseta", "t-shirt", "clothing"), ("suéter", "sweater", "clothing"),
    ("bata", "robe", "clothing"), ("delantal", "apron", "clothing"), ("pañuelo", "handkerchief", "clothing"),
    ("collar", "necklace", "clothing"), ("pulsera", "bracelet", "clothing"), ("anillo", "ring", "clothing"),
    ("arete", "earring", "clothing"), ("reloj de pulsera", "wristwatch", "clothing"), ("cremallera", "zipper", "clothing"),
    ("gerente", "manager", "work"), ("director", "director", "work"), ("secretario", "secretary", "work"),
    ("contador", "accountant", "work"), ("abogado", "lawyer", "work"), ("ingeniero", "engineer", "work"),
    ("arquitecto", "architect", "work"), ("periodista", "journalist", "work"), ("vendedor", "salesperson", "work"),
    ("obrero", "laborer", "work"), ("granjero", "farmer", "work"), ("cocinero", "cook", "work"),
    ("mesero", "waiter", "work"), ("cajero", "cashier", "work"), ("piloto", "pilot", "work"),
    ("conductor", "driver", "work"), ("carpintero", "carpenter", "work"), ("electricista", "electrician", "work"),
    ("plomero", "plumber", "work"), ("panadero", "baker", "work"),
    ("aula", "classroom", "school"), ("director escolar", "principal", "school"), ("recreo", "recess", "school"),
    ("uniforme escolar", "school uniform", "school"), ("regla", "ruler", "school"), ("goma", "eraser", "school"),
    ("tijeras escolares", "school scissors", "school"), ("carpeta", "folder", "school"), ("horario escolar", "class schedule", "school"),
    ("beca", "scholarship", "school"), ("título", "degree / title", "school"), ("diploma", "diploma", "school"),
    ("graduación", "graduation", "school"), ("biología", "biology", "school"), ("física", "physics", "school"),
    ("química", "chemistry", "school"), ("geografía", "geography", "school"), ("literatura", "literature", "school"),
    ("filosofía", "philosophy", "school"), ("educación física", "physical education", "school"),
    ("madrugada", "early morning / dawn", "time"), ("mediodía", "midday", "time"), ("medianoche", "midnight", "time"),
    ("ayer", "yesterday", "time"), ("hoy", "today", "time"), ("pasado mañana", "day after tomorrow", "time"),
    ("década", "decade", "time"), ("aniversario", "anniversary", "time"), ("cumpleaños", "birthday", "time"),
    ("horario de verano", "summer schedule", "time"),
    ("chubasco", "shower (rain)", "weather"), ("brisa", "breeze", "weather"), ("tormenta eléctrica", "thunderstorm", "weather"),
    ("sequía", "drought", "weather"), ("inundación", "flood", "weather"), ("terremoto", "earthquake", "weather"),
    ("monzón", "monsoon", "weather"), ("pronóstico", "forecast", "weather"),
    ("aplicación móvil", "mobile app", "technology"), ("navegador", "browser", "technology"), ("nube (datos)", "cloud (data)", "technology"),
    ("altavoz", "speaker", "technology"), ("auricular", "headphone", "technology"), ("micrófono", "microphone", "technology"),
    ("robot", "robot", "technology"), ("satélite", "satellite", "technology"), ("chip", "chip", "technology"),
    ("servidor", "server", "technology"), ("enlace", "link", "technology"), ("usuario", "user", "technology"),
    ("actualización", "update", "technology"), ("copia de seguridad", "backup", "technology"),
    ("voleibol", "volleyball", "sports"), ("béisbol", "baseball", "sports"), ("golf", "golf", "sports"),
    ("esquí", "skiing", "sports"), ("surf", "surfing", "sports"), ("atletismo", "athletics", "sports"),
    ("árbitro", "referee", "sports"), ("uniforme deportivo", "sports uniform", "sports"), ("silbato", "whistle", "sports"),
    ("torneo", "tournament", "sports"),
    ("compasión", "compassion", "emotions"), ("gratitud", "gratitude", "emotions"), ("confianza", "trust / confidence", "emotions"),
    ("decepción", "disappointment", "emotions"), ("frustración", "frustration", "emotions"), ("alivio", "relief", "emotions"),
    ("curiosidad", "curiosity", "emotions"), ("soledad", "loneliness", "emotions"), ("empatía", "empathy", "emotions"),
    ("dorado", "golden", "colors"), ("plateado", "silver (color)", "colors"), ("celeste", "sky blue", "colors"),
    ("turquesa", "turquoise", "colors"), ("beige", "beige", "colors"), ("violeta", "violet", "colors"),
    ("evento", "event", "general"), ("plan", "plan", "general"), ("meta", "goal", "general"),
    ("objetivo", "objective", "general"), ("logro", "achievement", "general"), ("suerte", "luck", "general"),
    ("aventura personal", "personal adventure", "general"), ("misterio", "mystery", "general"), ("secreto", "secret", "general"),
    ("verdad", "truth", "general"), ("mentira", "lie", "general"), ("costumbre", "custom / habit", "general"),
    ("tradición", "tradition", "general"), ("símbolo", "symbol", "general"), ("señal", "sign / signal", "general"),
    ("bandera", "flag", "general"), ("mapa mundial", "world map", "general"), ("continente", "continent", "general"),
    ("hemisferio", "hemisphere", "general"), ("universo", "universe", "general"),
]

VERB_CATEGORY_FALLBACK = "general"


TARGET_WORD_COUNT = 1000


def _round_robin_by_category(entries):
    """Groups (spanish, english, category) tuples by category (first-seen order)
    and interleaves them, so trimming to a fixed total keeps every category
    represented instead of chopping off whichever ones were listed last."""
    by_category = {}
    for entry in entries:
        by_category.setdefault(entry[2], []).append(entry)
    queues = list(by_category.values())
    ordered = []
    while queues:
        next_round = []
        for queue in queues:
            ordered.append(queue.pop(0))
            if queue:
                next_round.append(queue)
        queues = next_round
    return ordered


def build_words():
    """Returns (list of word dicts, set of infinitives that are verbs)."""
    seen = set()
    words = []
    verb_infinitives = []
    word_id = 1

    for spanish, english, category in VERBS:
        if spanish in seen:
            continue
        seen.add(spanish)
        present = conjugate_present(spanish)
        example = verb_example(spanish, present, word_id)
        words.append({
            "id": word_id, "spanish": spanish, "english": english,
            "partOfSpeech": "verb", "example": example, "category": category,
        })
        verb_infinitives.append((word_id, spanish))
        word_id += 1

    # Cap nouns so the dataset lands on TARGET_WORD_COUNT total, spreading the
    # cut evenly across categories (round-robin) instead of truncating the
    # tail of the NOUNS list, which would wipe out whole categories.
    noun_budget = max(0, TARGET_WORD_COUNT - len(words))
    nouns_added = 0
    for spanish, english, category in _round_robin_by_category(NOUNS):
        if nouns_added >= noun_budget:
            break
        if spanish in seen:
            continue
        seen.add(spanish)
        example = noun_example(spanish, word_id)
        words.append({
            "id": word_id, "spanish": spanish, "english": english,
            "partOfSpeech": "noun", "example": example, "category": category,
        })
        word_id += 1
        nouns_added += 1

    return words, verb_infinitives


def build_conjugations(verb_infinitives):
    conjugations = []
    for word_id, infinitive in verb_infinitives:
        present = conjugate_present(infinitive)
        preterite = conjugate_preterite(infinitive)
        conjugations.append({
            "wordId": word_id,
            "present": dict(zip(PERSONS, present)),
            "preterite": dict(zip(PERSONS, preterite)),
        })
    return conjugations


def main():
    words, verb_infinitives = build_words()
    conjugations = build_conjugations(verb_infinitives)

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "words.json"), "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT_DIR, "conjugations.json"), "w", encoding="utf-8") as f:
        json.dump(conjugations, f, ensure_ascii=False, indent=2)

    verbs = sum(1 for w in words if w["partOfSpeech"] == "verb")
    nouns = sum(1 for w in words if w["partOfSpeech"] == "noun")
    print(f"Wrote {len(words)} words ({verbs} verbs, {nouns} nouns) to {OUT_DIR}/words.json")
    print(f"Wrote {len(conjugations)} verb conjugations to {OUT_DIR}/conjugations.json")

    by_category = {}
    for w in words:
        by_category[w["category"]] = by_category.get(w["category"], 0) + 1
    for cat, count in sorted(by_category.items(), key=lambda kv: -kv[1]):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
