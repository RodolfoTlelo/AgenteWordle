# Wordle Agent – Proyecto Final IA

Agente inteligente que resuelve el juego **Wordle** usando maximización de entropía (Ganancia de Información esperada).

---

## Descripción del proyecto

El agente implementa la arquitectura propuesta en la Actividad 2:

```
Percepción → Estado → Decisión → Acción
```

| Componente | Implementación |
|------------|----------------|
| **Estado** `S = (V, H)` | `V` – set de palabras candidatas; `H` – historial de intentos + patrones de color |
| **Acción** `a` | Palabra de 5 letras elegida para ingresar al tablero |
| **Decisión** `a* = argmax f(s, a)` | Entropía de Shannon sobre la distribución de patrones de color posibles |
| **Conocimiento** | Lógica proposicional: eliminación dura de candidatos incompatibles con el feedback recibido |

### Función de decisión

Para cada palabra candidata `a`, se calcula:

```
H(a) = - Σ  p(pattern_k) * log2( p(pattern_k) )
```

donde `p(pattern_k)` es la proporción de palabras restantes en `V` que generarían el patrón `k` al evaluarse contra `a`. La palabra que **maximiza** esta entropía produce la mayor reducción esperada del espacio de búsqueda.

---

## Estructura del proyecto

```
wordle_agent/
├── src/
│   ├── vocabulary.py   # Carga y parseo del dataset CSV
│   ├── state.py        # Definición de S=(V,H), get_pattern(), filter_vocabulary()
│   ├── decision.py     # f(s,a) – entropía esperada y selección de la mejor acción
│   ├── agent.py        # Clase WordleAgent (percepción + estado + decisión)
│   └── play.py         # CLI interactivo y modo auto (self-play)
├── data/
│   └── 5_letters.csv   # Dataset: 2499 palabras de 5 letras en inglés
├── experiments/
│   └── evaluate.py     # Experimento batch con métricas
├── results/            # JSONs generados por evaluate.py
└── README.md
```

---

## Dependencias

Solo librería estándar de Python 3.10+. No se requieren paquetes externos.

```
python >= 3.10
```

---

## Cómo ejecutar

### 1. Modo interactivo / asistido

El agente sugiere la mejor palabra en cada turno. Tú juegas en Wordle y le das el feedback de colores.

```bash
cd wordle_agent/src
python play.py
```

**Formato del feedback** (5 caracteres):
- `g` = verde (letra correcta en posición correcta)
- `y` = amarillo (letra correcta, posición incorrecta)
- `b` = gris (letra no está en la palabra)

Ejemplo: si la retroalimentación fue ⬜🟨🟩⬜🟨 → escribe `b y g b y`

---

### 2. Modo automático (self-play)

El agente juega solo contra una palabra aleatoria del vocabulario.

```bash
cd wordle_agent/src
python play.py --auto
```

Con palabra específica:

```bash
python play.py --auto --secret crane
```

---

### 3. Experimento batch (métricas)

```bash
cd wordle_agent/experiments
python evaluate.py --n 200 --seed 42
```

Opciones:
- `--n 500`   → probar con 500 palabras aleatorias
- `--seed 42` → resultado reproducible
- `--full`    → probar el vocabulario completo (~2499 palabras, tarda ~10 min)

Los resultados se guardan en `results/` como JSON.

---

## Ejemplo de ejecución (modo auto)

```
==========================================
  AUTO MODE  |  Secret: ?????  (hidden)
==========================================

  Turn 1: [G] C  [Y] R  [B] A  [B] N  [B] E  |  candidates left: 87
  Turn 2: [G] C  [G] O  [G] U  [G] L  [G] D  |  candidates left: 1
  Turn 3: ...

  ✅  Solved 'COULD' in 3 attempt(s)!
```

---

## Métricas esperadas

Sobre 200 palabras aleatorias con seed=42:

| Métrica | Valor típico |
|---------|--------------|
| Win rate | ~98–100 % |
| Promedio de intentos | ~3.6–3.9 |
| Tiempo de decisión promedio | <50 ms / turno |

---

## Arquitectura – decisión tree (simplificada)

```
Estado inicial V (2499 palabras)
        │
        ▼  Turno 1: a* = "crane"  (alta entropía por defecto)
   Percepción (5 colores)
        │
        ▼  Filtrar V → V' ⊆ V
   |V'| ≤ 6? ──Yes──► Evaluar solo candidatos
        │ No
        ▼  Evaluar vocabulario completo, bonus a candidatos
   a* = argmax H(a)
        │
        ▼  ... repetir hasta verde×5 o 6 intentos
```

---

## Limitaciones

- El cálculo de entropía sobre el vocabulario completo (turno 2+) puede tardar ~0.5–2 seg por turno en hardware modesto.
- El agente no tiene en modo difícil de Wordle (donde los intentos deben usar las letras ya reveladas); añadirlo requeriría restringir `search_space = candidates` siempre.
- El dataset de 2499 palabras es el vocabulario *posible* de Wordle; el juego real usa un subconjunto de ~2315 palabras objetivo.
