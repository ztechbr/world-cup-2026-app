# Guia de Implementação: App Wear OS (Kotlin) - Copa 2026

Este documento fornece instruções passo a passo para criar o aplicativo circular de Copa do Mundo de 2026 em Kotlin para relógios inteligentes (Wear OS) utilizando **Jetpack Compose for Wear OS** no Android Studio.

---

## 🛠️ 1. Configuração do Projeto no Android Studio

1. Abra o **Android Studio** e selecione **New Project**.
2. Escolha o template **Wear OS** -> **Empty Compose Activity**.
3. Nomeie o projeto (ex: `WorldCupWearOS`) e selecione a linguagem **Kotlin**.
4. Certifique-se de que a API mínima seja pelo menos **API 30 (Android 11)** para amplo suporte ao Compose.

### Dependências Recomendadas (`build.gradle.kts`)
Adicione as dependências essenciais do Jetpack Compose para Wear OS:

```kotlin
dependencies {
    // Wear OS Compose Foundation & Material
    implementation("androidx.wear.compose:compose-material:1.3.1")
    implementation("androidx.wear.compose:compose-foundation:1.3.1")
    
    // Navegação Wear OS (suporta gesto de swipe para voltar nativo)
    implementation("androidx.wear.compose:compose-navigation:1.3.1")
    
    // Chamadas de rede HTTP e JSON
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    
    // Coroutines & Lifecycle
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.6.2")
}
```

---

## 🎨 2. Componentes de UI e Estilo Circular

O Jetpack Compose para Wear OS possui componentes especializados que otimizam o layout para telas circulares, evitando o corte de textos nas bordas.

### Tema de Cores (Dark Mode & Neon)
Crie o arquivo de tema em `Theme.kt`:

```kotlin
import androidx.compose.ui.graphics.Color
import androidx.wear.compose.material.Colors

val WearGreenAccent = Color(0xFF00FF87)
val WearBackground = Color(0xFF000000)
val WearCardBackground = Color(0xFF141416)
val WearTextPrimary = Color(0xFFFFFFFF)
val WearTextSecondary = Color(0xFF94A3B8)

val WearColorPalette = Colors(
    primary = WearGreenAccent,
    secondary = WearCardBackground,
    background = WearBackground,
    onPrimary = Color.Black,
    onSecondary = WearTextPrimary,
    onBackground = WearTextPrimary
)
```

---

## 🧭 3. Navegação Circular (Swipe to Dismiss)

No Wear OS, a navegação padrão de retorno é o gesto de deslizar da esquerda para a direita. O `SwipeDismissableNavHost` gerencia isso automaticamente:

```kotlin
import androidx.wear.compose.navigation.SwipeDismissableNavHost
import androidx.wear.compose.navigation.composable
import androidx.wear.compose.navigation.rememberSwipeDismissableNavController

@Composable
fun WearAppNavigation(viewModel: MatchViewModel) {
    val navController = rememberSwipeDismissableNavController()
    
    // Use Scaffold para manter o relógio (TimeText) fixo no topo da tela circular
    Scaffold(
        timeText = { TimeText() },
        vignette = { Vignette(vignettePosition = VignettePosition.TopAndBottom) },
        positionIndicator = { /* Indicador de scroll da página atual */ }
    ) {
        SwipeDismissableNavHost(
            navController = navController,
            startDestination = "main_carousel"
        ) {
            // Aba principal com as páginas horizontais deslizantes (Paises, Grupos, Jogos)
            composable("main_carousel") {
                MainCarouselScreen(viewModel, onNavigateToMatch = { matchId ->
                    navController.navigate("match_detail/$matchId")
                })
            }
            // Tela 4: Detalhes do Jogo selecionado
            composable("match_detail/{matchId}") { backStackEntry ->
                val matchId = backStackEntry.arguments?.getString("matchId")?.toIntOrNull()
                MatchDetailScreen(matchId, viewModel, onBack = {
                    navController.popBackStack()
                })
            }
        }
    }
}
```

---

## 📺 4. Estrutura das Telas em Wear OS

### Tela 1: Países (ScalingLazyColumn)
Usa o `ScalingLazyColumn` para reduzir o tamanho dos itens que estão saindo da borda superior/inferior da tela circular.

```kotlin
import androidx.wear.compose.material.ScalingLazyColumn
import androidx.wear.compose.material.items
import androidx.wear.compose.material.Chip
import androidx.wear.compose.material.ChipDefaults

@Composable
fun CountriesScreen(countries: List<Country>, onCountryClick: (String) -> Unit) {
    ScalingLazyColumn(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        item { ScreenHeader(title = "Países") }
        
        // Campo de busca (Pill shape)
        item {
            SearchChip(placeholder = "Buscar país...")
        }
        
        items(countries) { country ->
            Chip(
                onClick = { onCountryClick(country.name) },
                label = { Text(country.portugueseName) },
                secondaryLabel = { Text("${country.group} • ${country.points} pts") },
                icon = { Text(country.emoji, fontSize = 20.sp) },
                colors = ChipDefaults.primaryChipColors(
                    backgroundColor = WearCardBackground
                ),
                modifier = Modifier.fillMaxWidth().padding(horizontal = 10.dp)
            )
        }
    }
}
```

### Tela 2: Classificação por Grupos
Tabela otimizada de tamanho reduzido para exibição dentro do círculo.

```kotlin
@Composable
fun GroupStandingsCard(groupName: String, teams: List<TeamStanding>) {
    Card(
        onClick = {},
        modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp)
    ) {
        Column {
            Text("GRUPO $groupName", color = WearGreenAccent, style = MaterialTheme.typography.caption1)
            Spacer(modifier = Modifier.height(4.dp))
            teams.forEachIndexed { index, team ->
                Row(
                    modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text("${index + 1} ", color = Color.Gray)
                        Text("${team.emoji} ${team.name}")
                    }
                    Row {
                        Text("${team.jogos}  ", color = Color.LightGray)
                        Text("${team.vitorias}  ", color = Color.LightGray)
                        Text(team.pontos.toString(), fontWeight = FontWeight.Bold, color = Color.White)
                    }
                }
            }
        }
    }
}
```

### Tela 3: Jogos do Dia
Mostra a listagem de jogos com indicação de tempo real.

```kotlin
@Composable
fun MatchDayScreen(matches: List<Match>, onMatchClick: (Int) -> Unit) {
    ScalingLazyColumn(
        modifier = Modifier.fillMaxSize()
    ) {
        item { ScreenHeader("Jogos do Dia") }
        
        items(matches) { match ->
            TitleCard(
                onClick = { onMatchClick(match.id) },
                title = { Text("${match.homeCode} × ${match.awayCode}") },
                subtitle = { Text(match.stadium) }
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    if (match.status == "live") {
                        Text("AO VIVO", color = Color.Red, style = MaterialTheme.typography.caption2)
                    } else {
                        Text(match.time, color = Color.Gray)
                    }
                    Text(match.score ?: "vs", color = WearGreenAccent, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}
```

---

## 📡 5. Conexão HTTP (Retrofit) em Wear OS

Configuração do cliente HTTP com injeção automática de Token de segurança nos cabeçalhos:

```kotlin
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.GET

interface WorldCupApiService {
    @GET("matches")
    suspend fun getMatches(): List<MatchDto>
}

object RetrofitClient {
    private const val BASE_URL = "https://ai-worldcup26.jd0rwz.easypanel.host/"

    val instance: WorldCupApiService by lazy {
        val authInterceptor = Interceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("X-Token", "COPA26!")
                .build()
            chain.proceed(request)
        }

        val okHttpClient = OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .build()

        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(WorldCupApiService::class.java)
    }
}
```

---

## 🔄 6. Motor de Simulação (Coroutines & StateFlow)

Implementação do motor reativo usando Kotlin Coroutines na ViewModel para simulação em tempo real da rodada de jogos de "hoje":

```kotlin
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class MatchViewModel : ViewModel() {
    private val _matches = MutableStateFlow<List<Match>>(emptyList())
    val matches: StateFlow<List<Match>> = _matches

    private val _simMinute = MutableStateFlow(0)
    val simMinute: StateFlow<Int> = _simMinute

    private var simJob: Job? = null
    var isSimulating = MutableStateFlow(false)

    fun startSimulation(speedMs: Long = 500L) {
        if (isSimulating.value) return
        isSimulating.value = true
        
        simJob = viewModelScope.launch {
            // Altera jogos de hoje para "live"
            _matches.value = _matches.value.map { match ->
                if (match.date == "2026-06-14") match.copy(status = "live", score = "0-0") else match
            }
            
            for (minute in 1..90) {
                _simMinute.value = minute
                delay(speedMs) // Aceleração
                
                // Atualiza aleatoriamente os placares e eventos
                _matches.value = _matches.value.map { match ->
                    if (match.status == "live") {
                        val scoreParts = match.score?.split("-")?.map { it.toInt() } ?: listOf(0, 0)
                        var home = scoreParts[0]
                        var away = scoreParts[1]
                        
                        // Probabilidade de Gol (2% por minuto)
                        if (Math.random() < 0.02) {
                            if (Math.random() > 0.5) home++ else away++
                            
                            // Cria evento
                            val event = MatchEvent(minute, "goal", "Gol!")
                            match.copy(score = "$home-$away", events = match.events + event)
                        } else {
                            match
                        }
                    } else {
                        match
                    }
                }
            }
            
            // Finaliza jogos
            _matches.value = _matches.value.map { match ->
                if (match.status == "live") match.copy(status = "finished") else match
            }
            isSimulating.value = false
        }
    }

    fun stopSimulation() {
        simJob?.cancel()
        isSimulating.value = false
    }
}
```
