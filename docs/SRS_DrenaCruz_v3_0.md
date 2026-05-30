# Especificación de Requisitos de Software (SRS)
# DrenaCruz AI — Sistema de Alerta Temprana para Inundaciones Urbanas

---

<div align="center">

| Campo | Detalle |
| :--- | :--- |
| **Proyecto** | DrenaCruz AI |
| **Versión del Documento** | 3.0.0 |
| **Fecha de Emisión** | 30 de Mayo de 2026 |
| **Estándar de Referencia** | IEEE 830-1998 (Adaptado para Hackathon) |
| **Estado** | ✅ Aprobado — Versión de Ejecución |
| **Evento** | GDG Santa Cruz — Build with AI Hackathon 2026 |
| **Ubicación del Proyecto** | Santa Cruz de la Sierra, Bolivia |

</div>

---

## Historial de Revisiones

| Versión | Fecha | Cambios |
| :--- | :--- | :--- |
| 1.0.0 | 30/05/2026 | Documento inicial del MVP |
| 2.0.0 | 30/05/2026 | Reestructuración completa: RNF, RLS, tablas auxiliares, matriz de trazabilidad |
| 3.0.0 | 30/05/2026 | Incorporación del modelo White Label, separación Móvil/Web, estructura de repositorio monorepo, roles y flujos actualizados |

---

## Tabla de Contenidos

1. [Introducción](#1-introducción)
2. [Descripción General del Sistema](#2-descripción-general-del-sistema)
3. [Arquitectura del Proyecto](#3-arquitectura-del-proyecto)
4. [Producto 1 — App Móvil (Flutter)](#4-producto-1--app-móvil-flutter)
5. [Producto 2 — Panel Web (Administración)](#5-producto-2--panel-web-administración)
6. [Requisitos Funcionales](#6-requisitos-funcionales)
7. [Requisitos No Funcionales](#7-requisitos-no-funcionales)
8. [Modelo de Datos (Supabase)](#8-modelo-de-datos-supabase)
9. [Seguridad y Políticas RLS](#9-seguridad-y-políticas-rls)
10. [Inteligencia Artificial — Contrato con Gemini](#10-inteligencia-artificial--contrato-con-gemini)
11. [Modelo White Label](#11-modelo-white-label)
12. [Modelo de Negocio e Impacto](#12-modelo-de-negocio-e-impacto)
13. [Matriz de Trazabilidad](#13-matriz-de-trazabilidad)
14. [Criterios de Aceptación del Demo](#14-criterios-de-aceptación-del-demo)

---

## 1. Introducción

### 1.1 Propósito del Documento

Este documento es la **única fuente de verdad** del equipo DrenaCruz AI durante el hackathon. Define qué se construye, cómo se organiza el proyecto, quién hace qué y cómo se valida que el MVP está listo para el demo.

Cualquier decisión técnica, de diseño o de producto que no esté respaldada por una sección de este documento debe ser discutida en equipo antes de implementarse. Si una funcionalidad no aparece aquí, **no se implementa** en el hackathon.

### 1.2 Alcance del MVP

DrenaCruz AI es una **plataforma de dos productos** que trabajan en conjunto:

**Producto 1 — App Móvil (ciudadano):** Permite a cualquier persona reportar un canal obstruido con su teléfono, sin necesidad de crear una cuenta ni hacer login.

**Producto 2 — Panel Web (operador municipal):** Permite a funcionarios del municipio ver los reportes priorizados por IA, gestionar tareas de limpieza y cerrar incidentes desde un navegador web con login.

Ambos productos comparten la misma base de datos en Supabase y el mismo motor de IA (Gemini 1.5 Flash).

**Incluido en el MVP:**
- Reporte fotográfico ciudadano sin registro (móvil).
- Geolocalización automática por GPS del dispositivo.
- Análisis de imagen con IA y Score de Riesgo (1–10).
- Mapa de calor público visible desde la app móvil.
- Panel web con login para operadores municipales.
- Triage ordenado por riesgo y cierre de tareas.
- Personalización de marca por cliente (White Label básico).

**Fuera del alcance del MVP:**
- Notificaciones push.
- Predicción meteorológica.
- Analítica histórica avanzada.
- Soporte multi-ciudad simultáneo.
- App móvil para operadores (solo web en el MVP).

### 1.3 Definiciones y Glosario

| Término | Definición |
| :--- | :--- |
| **MVP** | Minimum Viable Product. Versión mínima funcional para el demo. |
| **SEARPI** | Servicio de Encauzamiento de Aguas y Regulación del Río Piraí. Cliente objetivo del MVP. |
| **SRS** | Software Requirements Specification. Este documento. |
| **RLS** | Row Level Security. Seguridad a nivel de fila en Supabase/PostgreSQL. Controla quién puede leer o escribir qué datos. |
| **White Label** | Modelo donde el producto se entrega sin marca propia para que el cliente lo use con su identidad corporativa. |
| **Score de Riesgo** | Número entero del 1 al 10 que representa el nivel de obstrucción de un canal. Lo calcula Gemini. |
| **Triage** | Proceso de ordenar y priorizar los reportes según su nivel de riesgo para atender primero los más críticos. |
| **Monorepo** | Repositorio único que contiene tanto el proyecto móvil como el web, compartiendo configuraciones comunes. |
| **B2G** | Business to Government. Venta a entidades gubernamentales como municipios. |
| **B2B** | Business to Business. Venta a empresas privadas como aseguradoras. |

### 1.4 Stack Tecnológico

| Capa | Tecnología | Notas |
| :--- | :--- | :--- |
| **App Móvil** | Flutter (Material Design 3) | Android e iOS desde un solo código |
| **Panel Web** | Flutter Web | Mismo código base que móvil, diferente target |
| **Base de Datos** | Supabase — PostgreSQL | Cloud, tier gratuito |
| **Almacenamiento** | Supabase Storage | Bucket `report-photos` |
| **Autenticación** | Supabase Auth | Anónimo para ciudadanos, email/password para operadores |
| **Inteligencia Artificial** | Google Gemini 1.5 Flash | Análisis de imagen vía REST API |
| **Mapas** | flutter_map + OpenStreetMap | Sin costo, sin clave de API de Google Maps |

> **Decisión de arquitectura:** Se usa Flutter tanto para móvil como para web. Esto significa que el equipo no necesita aprender dos tecnologías distintas. El mismo desarrollador puede trabajar en ambas plataformas.

---

## 2. Descripción General del Sistema

### 2.1 El Problema

Santa Cruz de la Sierra sufre inundaciones recurrentes en la época de lluvias (noviembre–marzo). La causa principal no es solo la lluvia: son los canales de drenaje tapados con basura, maleza y sedimentos que impiden que el agua fluya. El sistema actual es completamente **reactivo**: las cuadrillas de limpieza solo actúan después de que ya ocurrió la inundación y el daño está hecho.

### 2.2 La Solución

DrenaCruz AI convierte a los propios ciudadanos en sensores de campo. Con solo tomar una foto desde su teléfono, el vecino genera un reporte georreferenciado. La IA analiza la foto en segundos, asigna un nivel de riesgo y coloca el punto en un mapa. El municipio ve ese mapa en tiempo real y puede enviar cuadrillas a limpiar los canales más críticos **antes de que llegue la lluvia**.

```
ANTES (reactivo)              DESPUÉS con DrenaCruz AI (proactivo)
──────────────────────────    ──────────────────────────────────────────
Llueve → Canal desborda  →    Ciudadano reporta canal tapado
Inundación → Daños       →    IA analiza y asigna riesgo en segundos
Cuadrilla actúa tarde    →    Municipio limpia el canal antes de la lluvia
                              No hay inundación
```

### 2.3 Los Tres Actores del Sistema

#### Ciudadano / Vecino
El usuario más importante del sistema. No es técnico, puede tener cualquier edad, y no quiere complicaciones. Su único trabajo es tomar una foto y enviarla. El sistema debe ser tan simple que pueda hacerlo en menos de un minuto, parado frente al canal, con el teléfono en la mano.

- No crea cuenta, no hace login.
- Usa la app móvil.
- Puede ver el mapa de calor público.

#### Operador Municipal (SEARPI / Alcaldía)
El funcionario que recibe los reportes y coordina la limpieza. Trabaja desde una oficina o en campo con su computadora o tablet. Necesita una vista clara de qué canales son más urgentes.

- Tiene cuenta con email y contraseña.
- Usa el panel web.
- Puede ver todos los reportes, su foto, descripción de la IA y nivel de riesgo.
- Puede marcar reportes como "Limpiado".

#### Sistema de IA (Gemini Engine)
Actor no humano. Actúa de forma invisible cada vez que llega una foto nueva. Analiza la imagen, detecta el tipo de obstrucción y calcula el score de riesgo. El ciudadano y el operador nunca interactúan directamente con él.

### 2.4 Restricciones del Hackathon

| Restricción | Detalle |
| :--- | :--- |
| **Tiempo** | Máximo 24 horas de desarrollo |
| **Sin backend propio** | No se construye un servidor Node.js, Python ni similar. Supabase es el backend. |
| **Costo cero** | Solo se usan tiers gratuitos de Supabase y Google AI |
| **Alcance geográfico** | Solo Santa Cruz de la Sierra para el MVP |
| **Equipo pequeño** | Cada persona debe tener una responsabilidad clara (ver sección de estructura) |

---

## 3. Arquitectura del Proyecto

### 3.1 Visión General

El proyecto vive en un **monorepo**: una sola carpeta en el repositorio de Git que contiene todo. Esto facilita compartir configuraciones, modelos de datos y lógica común entre la app móvil y el panel web sin duplicar código.

```
drenacruz-ai/                    ← Raíz del repositorio
│
├── mobile/                      ← Producto 1: App Flutter para ciudadanos
├── web/                         ← Producto 2: Panel Flutter Web para operadores
├── supabase/                    ← Configuración de base de datos y seguridad
└── docs/                        ← Documentación del proyecto (este SRS, etc.)
```

### 3.2 Estructura Detallada de Carpetas

```
drenacruz-ai/
│
├── mobile/                                  ← APP MÓVIL (Flutter)
│   ├── lib/
│   │   ├── core/
│   │   │   ├── config/
│   │   │   │   └── app_config.dart          ← Configuración White Label (logo, nombre, colores)
│   │   │   ├── theme/
│   │   │   │   ├── app_colors.dart          ← Colores base del sistema de diseño
│   │   │   │   ├── app_typography.dart      ← Estilos de texto
│   │   │   │   └── app_theme.dart           ← ThemeData que consume app_config
│   │   │   ├── errors/
│   │   │   │   └── app_exception.dart       ← Clase única de errores del dominio
│   │   │   └── wrappers/
│   │   │       ├── database_wrapper.dart    ← Interfaz abstracta: base de datos
│   │   │       ├── storage_wrapper.dart     ← Interfaz abstracta: almacenamiento
│   │   │       └── ai_wrapper.dart          ← Interfaz abstracta: motor de IA
│   │   │
│   │   ├── features/
│   │   │   ├── report/                      ← MÓDULO: Reporte ciudadano
│   │   │   │   ├── data/                    ← Implementaciones concretas (Supabase, Gemini)
│   │   │   │   ├── domain/                  ← Entidad Report, casos de uso, interfaces
│   │   │   │   └── presentation/            ← Pantallas y controladores de estado
│   │   │   │       └── screens/
│   │   │   │           ├── home_screen.dart         ← Pantalla de inicio con botón Reportar
│   │   │   │           ├── camera_screen.dart       ← Cámara nativa
│   │   │   │           ├── preview_screen.dart      ← Previsualización antes de enviar
│   │   │   │           └── success_screen.dart      ← Confirmación de envío exitoso
│   │   │   │
│   │   │   └── map/                         ← MÓDULO: Mapa de calor público
│   │   │       ├── data/
│   │   │       ├── domain/
│   │   │       └── presentation/
│   │   │           └── screens/
│   │   │               └── map_screen.dart          ← Mapa con pines de riesgo
│   │   │
│   │   └── main.dart                        ← Punto de entrada + inyección de dependencias
│   │
│   ├── assets/
│   │   ├── images/
│   │   │   └── client_logo.png              ← Logo del cliente (White Label)
│   │   └── icons/
│   └── pubspec.yaml
│
├── web/                                     ← PANEL WEB (Flutter Web)
│   ├── lib/
│   │   ├── core/
│   │   │   ├── config/
│   │   │   │   └── app_config.dart          ← Misma configuración White Label
│   │   │   ├── theme/                       ← Mismo sistema de diseño que móvil
│   │   │   ├── errors/
│   │   │   └── wrappers/                    ← Mismas interfaces abstractas que móvil
│   │   │
│   │   ├── features/
│   │   │   ├── auth/                        ← MÓDULO: Login del operador
│   │   │   │   └── presentation/
│   │   │   │       └── screens/
│   │   │   │           └── login_screen.dart
│   │   │   │
│   │   │   ├── dashboard/                   ← MÓDULO: Panel principal
│   │   │   │   └── presentation/
│   │   │   │       └── screens/
│   │   │   │           └── dashboard_screen.dart    ← Vista general con métricas
│   │   │   │
│   │   │   ├── triage/                      ← MÓDULO: Lista de tareas ordenada por riesgo
│   │   │   │   └── presentation/
│   │   │   │       └── screens/
│   │   │   │           └── triage_screen.dart
│   │   │   │
│   │   │   └── map/                         ← MÓDULO: Mapa de calor para operador
│   │   │       └── presentation/
│   │   │           └── screens/
│   │   │               └── map_screen.dart
│   │   │
│   │   └── main.dart
│   │
│   └── pubspec.yaml
│
├── supabase/
│   ├── migrations/
│   │   ├── 001_create_reports_table.sql     ← Creación de tabla reports
│   │   ├── 002_create_operators_table.sql   ← Tabla de operadores municipales
│   │   ├── 003_create_views.sql             ← Vista active_risk_map
│   │   └── 004_rls_policies.sql             ← Todas las políticas de seguridad
│   └── seed/
│       └── demo_data.sql                    ← Datos de prueba para el demo del jurado
│
└── docs/
    ├── SRS_DrenaCruz_v3_0.md               ← Este documento
    └── PITCH_DECK.md                        ← Resumen para la presentación
```

### 3.3 Por Qué Esta Estructura

**Monorepo (una sola carpeta en Git) en lugar de dos repositorios separados:**
Permite que todo el equipo vea el proyecto completo, evita duplicar configuraciones y facilita que un desarrollador ayude en móvil o web según la necesidad del momento.

**Carpeta `supabase/` separada de las apps:**
Todo lo relacionado con la base de datos vive en un solo lugar. El compañero encargado de Supabase trabaja ahí sin tocar el código Flutter.

**Carpeta `core/wrappers/` en cada app:**
Todas las integraciones externas (Supabase SDK, Gemini SDK) están ocultas detrás de interfaces abstractas. Si mañana se cambia el proveedor de IA por otro, solo se modifica el wrapper, no toda la app.

**Carpeta `core/config/app_config.dart` en cada app:**
Aquí vive toda la configuración del cliente (logo, nombre, colores primarios). Para entregar el producto a otro cliente, solo se cambia este archivo. Es la base del modelo White Label.

### 3.4 Separación de Responsabilidades (SoC)

Cada capa tiene una responsabilidad única y no puede mezclarse con otra:

| Capa | Carpeta | Responsabilidad | Lo que NO debe hacer |
| :--- | :--- | :--- | :--- |
| **Presentación** | `presentation/` | Mostrar la UI y reaccionar a los 4 estados | Llamar a Supabase directamente |
| **Dominio** | `domain/` | Lógica de negocio pura, entidades, casos de uso | Importar cualquier SDK externo |
| **Datos** | `data/` | Comunicarse con wrappers para traer y guardar datos | Tener lógica de UI o negocio |
| **Wrappers** | `core/wrappers/` | Encapsular Supabase, Gemini y Storage | Contener lógica de negocio |

### 3.5 Los 4 Estados Obligatorios de Toda Pantalla

Toda pantalla en la app (móvil y web) debe manejar exactamente estos cuatro estados. Sin excepción.

| Estado | Cuándo aparece | Qué se muestra |
| :--- | :--- | :--- |
| **Loading** | Mientras se espera una respuesta de red o IA | Indicador de carga centrado en pantalla |
| **Error** | Cuando falla una operación de red o la IA | Mensaje legible para el usuario + botón "Reintentar" |
| **Empty** | Cuando la petición fue exitosa pero no hay datos | Ilustración + mensaje motivador + acción sugerida |
| **Data** | Cuando hay datos listos para mostrar | El contenido principal de la pantalla |

---

## 4. Producto 1 — App Móvil (Flutter)

### 4.1 Descripción General

La app móvil es el canal de entrada de datos al sistema. Es usada por ciudadanos y vecinos. Su principio de diseño central es **cero fricción**: el usuario no debe necesitar crear una cuenta, recordar contraseñas ni navegar menús complejos.

Al abrir la app, el ciudadano ve dos cosas: un botón grande para reportar y el mapa de calor de su ciudad.

### 4.2 Flujo Principal del Ciudadano

```
Abre la app
    ↓
Pantalla de Inicio
    ↓ presiona "Reportar Canal"
Cámara nativa del teléfono
    ↓ toma la foto
Pantalla de Previsualización
  (muestra foto + dirección aproximada detectada por GPS)
    ↓ presiona "Enviar Reporte"
   [Estado: Loading — "Analizando con IA..."]
    ↓ Supabase guarda la foto
    ↓ Gemini analiza la imagen
Pantalla de Éxito
  (muestra score de riesgo + categoría detectada)
    ↓
Vuelve al Inicio (mapa actualizado)
```

### 4.3 Pantallas de la App Móvil

| Pantalla | Propósito | Acceso |
| :--- | :--- | :--- |
| **Inicio** | Bienvenida con botón Reportar y acceso al mapa | Directo al abrir la app |
| **Cámara** | Captura fotográfica nativa del dispositivo | Desde botón Reportar |
| **Previsualización** | Muestra la foto tomada y la ubicación GPS antes de enviar | Después de capturar foto |
| **Éxito** | Confirmación visual con el resultado del análisis IA | Después de envío exitoso |
| **Mapa** | Mapa de calor con pines de riesgo de la ciudad | Desde botón Mapa en inicio |

### 4.4 Reglas de Experiencia de Usuario (Móvil)

- El botón "Reportar Canal" debe ser el elemento más visible de la pantalla de inicio. Grande, centrado, con color primario del cliente.
- El flujo completo de reporte (desde presionar el botón hasta la confirmación) debe completarse en menos de 4 pasos visibles para el usuario.
- Los mensajes de error deben estar en español simple, no en inglés técnico. Nunca mostrar mensajes de excepción del sistema.
- La app no debe pedir login en ningún momento durante el flujo del ciudadano.
- El estado `Loading` debe mostrar un mensaje descriptivo, no solo un spinner vacío. Ejemplo: "Analizando el canal con IA..." en lugar de solo un círculo girando.

---

## 5. Producto 2 — Panel Web (Administración)

### 5.1 Descripción General

El panel web es la herramienta de trabajo de los operadores municipales. A diferencia de la app móvil, aquí sí se requiere autenticación. El acceso está restringido a personas autorizadas por el municipio cliente.

El panel web se construye con **Flutter Web**, usando el mismo lenguaje y estructura que la app móvil para que el equipo no tenga que aprender tecnologías adicionales.

### 5.2 Flujo Principal del Operador

```
Abre el navegador (URL del panel del cliente)
    ↓
Pantalla de Login
  (email + contraseña, logo del cliente)
    ↓ autenticación exitosa
Dashboard Principal
  (métricas: total reportes, reportes críticos, limpiados hoy)
    ↓
Triage de Reportes
  (lista ordenada por risk_score descendente)
  Cada ítem muestra: foto miniatura, score con color, categoría, descripción IA, fecha
    ↓ operador revisa un reporte
    ↓ presiona "Marcar como Limpiado"
  Confirmación: "¿Confirmar que el canal fue limpiado?"
    ↓ confirma
  El reporte cambia a estado LIMPIADO
  El pin desaparece del mapa en tiempo real
```

### 5.3 Pantallas del Panel Web

| Pantalla | Propósito | Acceso |
| :--- | :--- | :--- |
| **Login** | Autenticación del operador con email/contraseña | URL raíz del panel |
| **Dashboard** | Vista general: contador de reportes críticos, moderados, limpiados hoy | Después del login |
| **Triage** | Lista de reportes activos ordenados por riesgo. Acción de cierre. | Menú lateral |
| **Mapa** | Mapa de calor con todos los reportes activos. Misma vista que el ciudadano pero con más información. | Menú lateral |

### 5.4 Reglas de Experiencia de Usuario (Web)

- La pantalla de login debe mostrar el logo del cliente (White Label), no el logo de DrenaCruz AI.
- El panel de triage debe mostrar siempre los reportes más críticos (riesgo 8–10) al inicio de la lista, sin necesidad de ordenarlos manualmente.
- Al marcar un reporte como limpiado, debe pedirse confirmación antes de ejecutar la acción. No se puede deshacer.
- El mapa y la lista de triage deben actualizarse automáticamente sin necesidad de recargar la página cuando llegan nuevos reportes.
- El diseño debe ser funcional en pantallas de computadora y tablet. No es prioridad adaptarlo a móvil en el MVP.

---

## 6. Requisitos Funcionales

### RF-01 — Reporte Ciudadano Sin Login

**Módulo:** App Móvil — Reporte
**Actor:** Ciudadano
**Prioridad:** Crítica

El ciudadano puede enviar un reporte fotográfico de un canal obstruido sin necesidad de crear una cuenta ni iniciar sesión. El sistema usa una sesión anónima de Supabase de forma transparente, sin que el usuario la vea ni interactúe con ella.

El reporte debe incluir obligatoriamente: la foto del canal y las coordenadas GPS del dispositivo en el momento de la captura.

**Resultado esperado:** Un registro nuevo aparece en la tabla `reports` de Supabase con `status = PENDIENTE`, la URL de la foto almacenada en Supabase Storage y las coordenadas geográficas reales.

**Condición de fallo manejada:** Si el GPS no está disponible, se advierte al usuario con un mensaje amigable pero el reporte puede enviarse igualmente con coordenadas en null. Si la subida de la foto falla, se muestra el estado de error con opción de reintentar.

---

### RF-02 — Análisis Automático con IA

**Módulo:** Motor de IA
**Actor:** Sistema (Gemini)
**Prioridad:** Crítica

Inmediatamente después de guardarse el reporte (RF-01), el sistema envía la imagen a la API de Gemini 1.5 Flash. Gemini analiza la foto y devuelve un objeto JSON con tres campos: `risk_score` (número del 0 al 10), `category` (tipo de obstrucción) y `ai_description` (resumen técnico en español de máximo 80 caracteres).

El sistema actualiza el registro del reporte en Supabase con esos tres valores.

**Resultado esperado:** El reporte en la base de datos tiene los tres campos de IA completados en menos de 8 segundos desde su creación.

**Condición de fallo manejada:** Si Gemini responde con `category: "no_valido"`, el reporte se marca como `INVALIDO` y se muestra al ciudadano un mensaje indicando que la foto no parece ser de un canal. Si la API no responde en 10 segundos, el reporte se guarda con `risk_score: null` para revisión manual posterior.

---

### RF-03 — Mapa de Calor Público

**Módulo:** Mapa (Móvil y Web)
**Actor:** Ciudadano y Operador
**Prioridad:** Crítica

El mapa muestra todos los reportes con `status = PENDIENTE` y `risk_score` calculado como pines de colores sobre el mapa de Santa Cruz de la Sierra. El código de colores es:

| Color | Rango | Nivel |
| :--- | :--- | :--- |
| 🔴 Rojo | 8 – 10 | Crítico — riesgo inminente de desborde |
| 🟡 Amarillo | 5 – 7 | Moderado — vigilar ante lluvias próximas |
| 🟢 Verde | 1 – 4 | Bajo — poca obstrucción, flujo normal |
| ⚪ Gris | null | Pendiente — IA aún procesando |

Al tocar un pin, aparece un popup con: miniatura de la foto, nivel de riesgo, categoría detectada y descripción de la IA.

**Resultado esperado:** El mapa carga y muestra los pines en menos de 3 segundos con conexión WiFi.

---

### RF-04 — Login del Operador Municipal

**Módulo:** Panel Web — Autenticación
**Actor:** Operador Municipal
**Prioridad:** Crítica

El panel web requiere autenticación obligatoria mediante email y contraseña antes de acceder a cualquier funcionalidad. La pantalla de login muestra el logo del cliente (White Label). Si el operador no tiene cuenta, no puede acceder: no hay opción de registro público.

Las cuentas de operadores son creadas directamente por el administrador en el panel de Supabase, no desde la aplicación.

**Resultado esperado:** Un operador con credenciales válidas accede al dashboard. Un intento con credenciales incorrectas muestra un mensaje de error claro.

---

### RF-05 — Panel de Triage y Cierre de Tareas

**Módulo:** Panel Web — Triage
**Actor:** Operador Municipal
**Prioridad:** Crítica

El operador ve una lista de todos los reportes con `status = PENDIENTE`, ordenados de mayor a menor `risk_score`. Puede ver la foto, descripción de la IA y nivel de riesgo de cada reporte. Puede marcar cualquier reporte como `LIMPIADO`, lo que actualiza su estado en la base de datos y lo elimina del mapa activo.

**Resultado esperado:** Al marcar como limpiado, el estado del reporte cambia en Supabase y el pin desaparece del mapa en tiempo real (menos de 5 segundos).

**Condición de vacío manejada:** Si no hay reportes pendientes, se muestra el estado `Empty` con el mensaje "Todos los canales están en orden".

---

## 7. Requisitos No Funcionales

### RNF-01 — Rendimiento

| ID | Requisito | Métrica objetivo |
| :--- | :--- | :--- |
| RNF-01.1 | Tiempo de análisis completo de IA | ≤ 8 segundos (p95) |
| RNF-01.2 | Carga inicial del mapa | ≤ 3 segundos en WiFi |
| RNF-01.3 | Subida de foto a Supabase Storage | ≤ 10 segundos para imagen ≤ 5 MB |
| RNF-01.4 | Respuesta de la UI a interacciones del usuario | ≤ 100 ms (sin I/O) |

### RNF-02 — Usabilidad

- Un ciudadano sin experiencia técnica debe poder enviar un reporte en ≤ 3 pasos visibles.
- Toda pantalla debe implementar los 4 estados: Loading, Error, Empty y Data.
- Los mensajes de error deben ser en español simple, comprensibles por cualquier persona.
- El código de colores del mapa (rojo/amarillo/verde) debe ser consistente en todas las pantallas de ambas aplicaciones.

### RNF-03 — Seguridad

- Las claves de API (Supabase URL, Supabase Anon Key, Gemini API Key) nunca deben estar escritas directamente en el código fuente. Deben usarse variables de entorno o configuración externa.
- Las políticas RLS de Supabase deben estar activas en todas las tablas.
- Los ciudadanos (sesión anónima) solo pueden crear reportes. No pueden modificar ni eliminar.
- Solo operadores con cuenta activa pueden actualizar el estado de los reportes.
- Nadie puede eliminar reportes desde la aplicación. Los registros son permanentes por integridad histórica.

### RNF-04 — Mantenibilidad

- Toda integración con SDK externo debe estar detrás de una interfaz abstracta en `core/wrappers/`.
- La configuración del cliente (logo, nombre, colores) debe estar centralizada en `core/config/app_config.dart`.
- Para entregar el producto a un nuevo cliente, solo se deben modificar: `app_config.dart`, `client_logo.png` y las credenciales de Supabase.

### RNF-05 — Confiabilidad

- Si la API de Gemini falla o hace timeout, el reporte se guarda igualmente en Supabase con `risk_score: null`. El sistema no pierde datos del ciudadano.
- La app móvil no debe mostrar errores técnicos ni excepciones al usuario final bajo ninguna circunstancia.
- Si el GPS no está disponible, la app advierte al usuario pero no bloquea el flujo de reporte.

---

## 8. Modelo de Datos (Supabase)

### 8.1 Tabla Principal: `reports`

Es el corazón del sistema. Almacena cada reporte enviado por un ciudadano, enriquecido por la IA.

| Columna | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Sí | Identificador único generado automáticamente |
| `created_at` | Timestamp | Sí | Fecha y hora de creación del reporte |
| `photo_url` | Texto | Sí | URL pública de la foto en Supabase Storage |
| `latitude` | Decimal | Sí | Latitud GPS del lugar donde se tomó la foto |
| `longitude` | Decimal | Sí | Longitud GPS del lugar donde se tomó la foto |
| `status` | Texto | Sí | Estado: `PENDIENTE`, `LIMPIADO` o `INVALIDO`. Default: `PENDIENTE` |
| `risk_score` | Entero | No | Score de riesgo del 0 al 10. Null hasta que Gemini procesa. |
| `category` | Texto | No | Tipo de obstrucción: `basura`, `maleza`, `sedimento`, `escombros`, `despejado`, `no_valido` |
| `ai_description` | Texto | No | Descripción técnica generada por Gemini. Máximo 80 caracteres. |
| `reported_by` | UUID | No | ID del usuario anónimo de Supabase que creó el reporte |
| `cleaned_at` | Timestamp | No | Fecha y hora en que el operador marcó como limpiado |
| `cleaned_by` | UUID | No | ID del operador que cerró el reporte |

### 8.2 Tabla: `operators`

Almacena el perfil extendido de los operadores municipales. Solo las personas registradas aquí pueden acceder al panel web.

| Columna | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `id` | UUID | Sí | Mismo ID que el usuario en Supabase Auth |
| `full_name` | Texto | Sí | Nombre completo del funcionario |
| `badge_id` | Texto | No | Número de legajo o carnet municipal |
| `is_active` | Booleano | Sí | Si está en false, no puede acceder aunque tenga cuenta. Default: true |
| `created_at` | Timestamp | Sí | Fecha de alta en el sistema |

### 8.3 Vista: `active_risk_map`

Una vista de solo lectura que el mapa usa para obtener únicamente los reportes pendientes con IA procesada. Agrega el campo `risk_level` para simplificar la lógica en la app.

Retorna: `id`, `photo_url`, `latitude`, `longitude`, `risk_score`, `category`, `ai_description`, `created_at`, y `risk_level` (valores: `CRITICO`, `MODERADO`, `BAJO`).

Solo incluye reportes con `status = PENDIENTE` y `risk_score` no nulo, ordenados por `risk_score` descendente.

---

## 9. Seguridad y Políticas RLS

Supabase permite definir reglas de seguridad a nivel de base de datos que se aplican sin importar desde dónde se haga la petición. Estas reglas son la última línea de defensa del sistema.

### Reglas para la tabla `reports`

| Operación | Quién puede | Condición |
| :--- | :--- | :--- |
| `INSERT` (crear) | Cualquier usuario, incluso anónimo | Sin condiciones. Cualquier persona puede reportar. |
| `SELECT` (leer) | Cualquier usuario, incluso anónimo | El mapa es público. Todos pueden ver los reportes. |
| `UPDATE` (modificar) | Solo operadores autenticados y activos | El usuario autenticado debe existir en la tabla `operators` con `is_active = true` |
| `DELETE` (eliminar) | Nadie | No se crea ninguna política de eliminación. |

### Reglas para la tabla `operators`

| Operación | Quién puede | Condición |
| :--- | :--- | :--- |
| `SELECT` (leer) | Solo el propio operador | Solo puede ver su propio registro. |
| `INSERT` / `UPDATE` / `DELETE` | Solo desde el panel de Supabase | No desde la app. Los administra el equipo técnico directamente. |

### Configuración del bucket `report-photos`

- Acceso de lectura: **público**. Cualquier persona puede ver las fotos (necesario para mostrarlas en el mapa).
- Acceso de escritura: **usuarios de Supabase** (incluyendo anónimos). Solo la app puede subir fotos, no cualquier persona con la URL del bucket.

---

## 10. Inteligencia Artificial — Contrato con Gemini

### 10.1 Comportamiento Esperado

Gemini actúa como el "DrenaCruz Engine": recibe una foto y devuelve exactamente tres datos. Nada más. El prompt del sistema está diseñado para que la respuesta sea siempre un objeto JSON válido, sin texto adicional, sin explicaciones, sin bloques de código Markdown.

### 10.2 System Prompt (Instrucción del Sistema)

Este es el texto que se configura como instrucción del sistema en la llamada a Gemini. Es fijo y no cambia entre llamadas.

---

*Eres "DrenaCruz Engine", un experto en ingeniería hidráulica urbana especializado en gestión de riesgos de inundación para Santa Cruz de la Sierra, Bolivia.*

*TU MISIÓN ÚNICA: Analizar fotografías de canales de drenaje urbano capturadas por ciudadanos con sus teléfonos. Determinar el nivel de obstrucción para prevenir inundaciones.*

*REGLA 1 — VALIDACIÓN: Si la foto NO muestra un canal, cuneta, alcantarilla o estructura de drenaje → devolver risk_score: 0, category: "no_valido".*

*REGLA 2 — CATEGORIZACIÓN: Identificar el tipo de obstrucción predominante: basura (plásticos, residuos sólidos), maleza (vegetación excesiva), sedimento (tierra, barro, arena), escombros (materiales de construcción, objetos voluminosos), despejado (canal limpio).*

*REGLA 3 — SCORE: 1–3 = flujo normal o mínimamente afectado. 4–7 = obstrucción parcial, dificultad de flujo. 8–10 = obstrucción severa o total, riesgo inminente de desborde.*

*REGLA 4 — DESCRIPCIÓN: Redactar en español, máximo 80 caracteres, solo hechos objetivos observables en la imagen.*

*FORMATO DE SALIDA: Responder ÚNICAMENTE con el objeto JSON. Sin texto adicional. Sin Markdown.*

*{ "risk_score": número, "category": "basura|maleza|sedimento|escombros|despejado|no_valido", "ai_description": "texto máximo 80 caracteres" }*

---

### 10.3 Ejemplos de Respuestas Válidas

**Canal bloqueado con basura:**
`risk_score: 9, category: "basura", ai_description: "Canal bloqueado al 85% por bolsas plásticas y residuos sólidos."`

**Canal con maleza moderada:**
`risk_score: 6, category: "maleza", ai_description: "Vegetación densa reduce la sección de flujo en aproximadamente 50%."`

**Canal limpio:**
`risk_score: 2, category: "despejado", ai_description: "Canal despejado, residuos mínimos sin impacto en el flujo hidráulico."`

**Foto inválida:**
`risk_score: 0, category: "no_valido", ai_description: "Imagen no corresponde a canal de drenaje urbano."`

### 10.4 Manejo de Errores de la API

| Situación | Qué hace la app |
| :--- | :--- |
| Respuesta exitosa con `no_valido` | Muestra mensaje al ciudadano. Marca reporte como `INVALIDO` en la base de datos. |
| Error 429 (rate limit) | Espera 30 segundos y reintenta una vez. |
| Error 400 (imagen muy grande) | Comprime la imagen a JPEG ≤ 1 MB y reintenta. |
| Error 500 (error interno de Gemini) | Guarda el reporte con `risk_score: null`. Informa al usuario que el análisis se completará después. |
| Timeout (más de 10 segundos) | Guarda el reporte con `risk_score: null`. El operador puede revisarlo manualmente. |

---

## 11. Modelo White Label

### 11.1 Qué Significa

DrenaCruz AI es el motor que funciona por detrás. El producto que el cliente compra y que los ciudadanos usan tiene el nombre, el logo y los colores del cliente. Esto se llama **White Label** o marca blanca.

Ejemplo: Si la Alcaldía de Santa Cruz compra el sistema, la app en el teléfono del ciudadano dirá "Sistema de Drenaje SEARPI", con el logo de la alcaldía. En ningún lugar visible aparece "DrenaCruz AI".

### 11.2 Por Qué Importa Para el Negocio

- El municipio puede presentarlo como su propia solución tecnológica ante los ciudadanos.
- Los reclamos ciudadanos van dirigidos al municipio, no al equipo de DrenaCruz AI.
- Permite vender el mismo producto a diferentes ciudades o clientes sin conflictos de marca.
- Aumenta la percepción de valor: el cliente no paga por una app genérica, paga por su plataforma personalizada.

### 11.3 Qué se Personaliza por Cliente

| Elemento | Descripción |
| :--- | :--- |
| **Logo** | Imagen del cliente en pantalla de inicio, login y splash screen |
| **Nombre de la app** | Título visible en la app y en el panel web |
| **Color primario** | Color principal de botones, íconos y elementos destacados |
| **Color secundario** | Color de acento y elementos secundarios |
| **Ciudad por defecto** | Coordenadas del centro del mapa al abrir la app |
| **Nombre del cliente** | Texto institucional en pies de página y pantalla de éxito |

### 11.4 Qué NO Cambia Entre Clientes

- La lógica del motor de IA y el prompt de Gemini.
- La estructura de la base de datos.
- El flujo de reportes y el sistema de triage.
- Las políticas de seguridad.

### 11.5 Cómo Se Implementa (Concepto)

Todo lo personalizable vive en un único archivo de configuración por aplicación: `core/config/app_config.dart`. Para entregar el producto a un nuevo cliente, el equipo solo modifica ese archivo y reemplaza el logo. No se toca ninguna otra parte del código.

---

## 12. Modelo de Negocio e Impacto

### 12.1 Propuesta de Valor

> *"Convertimos a cada ciudadano de Santa Cruz en un sensor inteligente de inundaciones, y a la IA en el analista 24/7 que la Alcaldía no puede costear."*

### 12.2 Modelos de Ingresos

**B2G — Licencia Municipal (ingreso principal):**
Venta de licencia SaaS anual a municipios, incluyendo el panel operativo, la app móvil con su marca y soporte técnico. El argumento económico es directo: una sola inundación severa destruye infraestructura por millones de bolivianos. El costo de la licencia es marginal comparado con ese gasto de emergencia.

**B2B — Datos de Riesgo (ingreso secundario):**
Venta de datos históricos agregados y anonimizados por zona geográfica a aseguradoras locales. Les permite calcular primas de seguro de propiedad con mayor precisión en zonas de riesgo hídrico.

**Escalabilidad:**
El mismo producto se puede vender a cualquier municipio de Bolivia o Latinoamérica con canales de drenaje. Para cada nuevo cliente, solo se configura el White Label, se apunta a una instancia de Supabase nueva y se despliega. No se reescribe código.

### 12.3 Triple Impacto

| Dimensión | Impacto Concreto |
| :--- | :--- |
| 🤝 **Social** | Vecinos de zonas bajas reciben alertas visuales antes de que llueva. Prevención de pérdidas materiales y riesgo de vidas. |
| 🌿 **Ambiental** | Retiro planificado de plásticos y sedimentos antes de que las lluvias los arrastren al Río Piraí y contaminen sus riberas. |
| 💰 **Económico** | Reducción del gasto municipal reactivo en emergencias, reparación de asfalto y daños a infraestructura causados por aguas acumuladas. |

---

## 13. Matriz de Trazabilidad

Cada requisito está vinculado a su implementación. Si un miembro del equipo trabaja en una pantalla, puede ver aquí qué requisito está cumpliendo y qué tabla de Supabase afecta.

| Requisito | Aplicación | Pantalla / Componente | Tabla Supabase | Actor |
| :--- | :--- | :--- | :--- | :--- |
| RF-01: Reporte sin login | Móvil | `camera_screen`, `preview_screen`, `success_screen` | `reports` (INSERT) | Ciudadano |
| RF-02: Análisis IA | Móvil | `ai_wrapper` (llamada tras RF-01) | `reports` (UPDATE) | Sistema (Gemini) |
| RF-03: Mapa de calor | Móvil + Web | `map_screen` | `active_risk_map` (SELECT) | Ciudadano + Operador |
| RF-04: Login operador | Web | `login_screen` | `operators` (SELECT) | Operador |
| RF-05: Triage y cierre | Web | `triage_screen` | `reports` (SELECT + UPDATE) | Operador |
| White Label: Config | Móvil + Web | `app_config.dart`, `app_theme.dart` | — | Equipo técnico |
| RLS: Ciudadano anónimo | — | — | Política INSERT en `reports` | Supabase |
| RLS: Operador | — | — | Política UPDATE en `reports` | Supabase |

---

## 14. Criterios de Aceptación del Demo

El MVP está listo para presentar ante el jurado cuando cumple **todos** estos criterios. Usarlos como checklist antes del demo.

| # | Criterio | Cómo verificarlo |
| :--- | :--- | :--- |
| ✅ DA-01 | Un ciudadano envía un reporte real desde el teléfono físico durante el demo, sin hacer login | Demo en vivo con teléfono en mano |
| ✅ DA-02 | La foto aparece en Supabase Storage en menos de 10 segundos | Abrir Supabase Dashboard en pantalla del jurado |
| ✅ DA-03 | El reporte en la base de datos tiene `risk_score`, `category` y `ai_description` completados | Verificar en tabla `reports` de Supabase |
| ✅ DA-04 | El mapa muestra al menos 3 marcadores de colores distintos (rojo, amarillo, verde) | Vista del mapa en la app, con datos de prueba precargados |
| ✅ DA-05 | El operador hace login en el panel web, ve el triage y marca un reporte como limpiado | Demo del flujo completo end-to-end |
| ✅ DA-06 | Al marcar como limpiado, el pin desaparece del mapa en tiempo real | Ambas pantallas visibles simultáneamente |
| ✅ DA-07 | El panel web muestra el logo del cliente (White Label), no "DrenaCruz AI" | Observable visualmente |
| ✅ DA-08 | La app no crashea ni muestra errores técnicos durante todo el flujo del demo | Prueba completa sin interrupciones previas al demo |
| ✅ DA-09 | Toda pantalla muestra el estado Loading durante operaciones de red | Observable durante el demo en vivo |

---

*Documento oficial del equipo DrenaCruz AI*
*Hackathon "Build with AI" — GDG Santa Cruz 2026*
*Versión 3.0.0 — Estado: Aprobado para ejecución*
