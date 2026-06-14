# Guia de Implementação: App Mobile Android (Kotlin + Jetpack Compose)

Este documento fornece instruções detalhadas para criar o aplicativo da Copa do Mundo 2026 em Kotlin para celulares Android usando **Jetpack Compose** no Android Studio.

---

## 🛠️ 1. Configuração do Projeto

1. Abra o **Android Studio** -> **New Project** -> **Empty Compose Activity**.
2. Linguagem: **Kotlin**.
3. API Mínima Recomendada: **API 24 (Android 7.0)** ou superior.

### Dependências (`build.gradle.kts`)
Adicione as dependências essenciais do Jetpack Compose, Navegação e HTTP:

```kotlin
dependencies {
    // Material Design 3
    implementation("androidx.compose.material3:material3:1.2.0")
    implementation("androidx.compose.ui:ui-tooling-preview")
    
    // Navegação Mobile
    implementation("androidx.navigation:navigation-compose:2.7.7")
    
    // Retrofit HTTP & Coroutines Flow
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.6.2")
}
```

---

## 🎨 2. Sistema de Design (Tema Dark & Neon)

Crie as cores e o tema em `Color.kt` e `Theme.kt`:

```kotlin
// Cores (Color.kt)
val DarkBackground = Color(0xFF09090B)
val CardBackground = Color(0xFF141416)
val AccentNeonGreen = Color(0xFF00FF87)
val TextPrimary = Color(0xFFFFFFFF)
val TextSecondary = Color(0xFF94A3B8)
val BorderColor = Color(0xFF27272A)

// Tema (Theme.kt)
private val DarkColorScheme = darkColorScheme(
    primary = AccentNeonGreen,
    background = DarkBackground,
    surface = CardBackground,
    onPrimary = Color.Black,
    onBackground = TextPrimary,
    onSurface = TextPrimary
)
```

---

## 🧭 3. Navegação por Abas (Bottom Navigation)

Crie a barra de navegação principal no rodapé da tela:

```kotlin
sealed class Screen(val route: String, val title: String, val icon: String) {
    object Countries : Screen("countries", "Países", "🏳️")
    object Groups : Screen("groups", "Grupos", "📊")
    object Matches : Screen("matches", "Jogos", "⚽")
}

@Composable
fun MainMobileScreen(viewModel: MatchViewModel) {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    Scaffold(
        bottomBar = {
            NavigationBar(containerColor = CardBackground) {
                val items = listOf(Screen.Countries, Screen.Groups, Screen.Matches)
                items.forEach { screen ->
                    NavigationBarItem(
                        selected = currentRoute == screen.route,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) { saveState = true }
                                launchSingleTop = true
                                restoreState = true
                            }
                        },
                        label = { Text(screen.title) },
                        icon = { Text(screen.icon, fontSize = 20.sp) }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Screen.Countries.route,
            modifier = Modifier.padding(innerPadding)
        ) {
            composable(Screen.Countries.route) { CountriesScreen(viewModel, navController) }
            composable(Screen.Groups.route) { GroupsScreen(viewModel, navController) }
            composable(Screen.Matches.route) { MatchesScreen(viewModel, navController) }
            composable("match_detail/{matchId}") { backStackEntry ->
                val id = backStackEntry.arguments?.getString("matchId")?.toIntOrNull()
                MatchDetailScreen(id, viewModel, onBack = { navController.popBackStack() })
            }
        }
    }
}
```

---

## 📱 4. Telas do App Mobile (Jetpack Compose)

### Tela 1: Países (Filtro e Busca)

```kotlin
@Composable
fun CountriesScreen(viewModel: MatchViewModel, navController: NavController) {
    val countries by viewModel.countries.collectAsState()
    var searchQuery by remember { mutableStateOf("") }
    var selectedContinent by remember { mutableStateOf("Todos") }

    Column(modifier = Modifier.fillMaxSize().background(DarkBackground).padding(16.dp)) {
        Text("Países", style = MaterialTheme.typography.headlineLarge, fontWeight = FontWeight.Bold)
        
        // Campo de Busca
        OutlinedTextField(
            value = searchQuery,
            onValueChange = { searchQuery = it },
            placeholder = { Text("Buscar país...") },
            modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
            shape = RoundedCornerShape(28.dp),
            colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = AccentNeonGreen)
        )

        // Filtro Horizontal de Continentes
        LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            val continents = listOf("Todos", "Sul-Am.", "Europa", "Caribe/C", "África", "Ásia", "Oceania")
            items(continents) { continent ->
                val active = selectedContinent == continent
                FilterChip(
                    selected = active,
                    onClick = { selectedContinent = continent },
                    label = { Text(continent) }
                )
            }
        }

        // Lista de Países
        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxSize()) {
            items(countries.filter { 
                (selectedContinent == "Todos" || it.region == selectedContinent) &&
                (searchQuery.isEmpty() || it.portugueseName.contains(searchQuery, ignoreCase = true))
            }) { country ->
                CountryCard(country, onClick = { navController.navigate("match_detail/${country.matchId}") })
            }
        }
    }
}
```

### Tela 2: Classificação Dinâmica dos Grupos

```kotlin
@Composable
fun GroupsScreen(viewModel: MatchViewModel, navController: NavController) {
    val standings by viewModel.standings.collectAsState()

    LazyColumn(
        modifier = Modifier.fillMaxSize().background(DarkBackground).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        item {
            Text("Grupos da Copa", style = MaterialTheme.typography.headlineLarge, fontWeight = FontWeight.Bold)
        }

        standings.forEach { (groupName, teams) ->
            item {
                ElevatedCard(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.elevatedCardColors(containerColor = CardBackground)
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text("GRUPO $groupName", color = AccentNeonGreen, fontWeight = FontWeight.Bold)
                            Text("J   V   P", color = TextSecondary, style = MaterialTheme.typography.bodySmall)
                        }
                        Divider(modifier = Modifier.padding(vertical = 8.dp), color = BorderColor)
                        
                        teams.forEachIndexed { index, team ->
                            Row(
                                modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text("${index + 1} ", color = TextSecondary)
                                    Text("${team.emoji} ${team.name}", color = TextPrimary)
                                }
                                Row {
                                    Text("${team.J}   ", color = TextSecondary)
                                    Text("${team.V}   ", color = TextSecondary)
                                    Text(team.P.toString(), color = TextPrimary, fontWeight = FontWeight.Bold)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
```

### Tela 3: Jogos do Dia (Live & Agendados)

```kotlin
@Composable
fun MatchesScreen(viewModel: MatchViewModel, navController: NavController) {
    val matches by viewModel.matches.collectAsState()
    val todayMatches = matches.filter { it.date == "2026-06-14" }

    LazyColumn(
        modifier = Modifier.fillMaxSize().background(DarkBackground).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item {
            Text("Jogos do Dia", style = MaterialTheme.typography.headlineLarge, fontWeight = FontWeight.Bold)
        }

        // Seção Ao Vivo
        val live = todayMatches.filter { it.status == "live" }
        if (live.isNotEmpty()) {
            item { Text("AO VIVO", color = Color.Red, fontWeight = FontWeight.Bold) }
            items(live) { match ->
                MatchCard(match, onClick = { navController.navigate("match_detail/${match.id}") })
            }
        }

        // Seção Agendados / Terminados
        val scheduled = todayMatches.filter { it.status != "live" }
        if (scheduled.isNotEmpty()) {
            item { Text("OUTROS JOGOS", color = TextSecondary, fontWeight = FontWeight.Bold) }
            items(scheduled) { match ->
                MatchCard(match, onClick = { navController.navigate("match_detail/${match.id}") })
            }
        }
    }
}
```

---

## 📡 5. Chamada de API Segura (Retrofit Client)

Interseptador de cabeçalho padrão para autenticação automática com token `COPA26!`:

```kotlin
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ApiClient {
    private const val BASE_URL = "https://ai-worldcup26.jd0rwz.easypanel.host/"

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor { chain ->
            val original = chain.request()
            val request = original.newBuilder()
                .header("X-Token", "COPA26!")
                .method(original.method, original.body)
                .build()
            chain.proceed(request)
        }
        .build()

    val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
}
```
