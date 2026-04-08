# Diagrama de actividad
Flujo general end-to-end
```mermaid
flowchart TD
    A[RRHH crea encuesta] --> B[Líder avala encuesta]
	B --> Z[Lider flaggea empleados]
    Z --> C[Encuesta activa]
	
    C --> D[Trabajador responde encuesta]
    D --> E[Validación de respuestas]
    E --> F[Almacenamiento en BD - Respuestas]

    F --> G[Extracción de datos]
    G --> H[Procesamiento y transformación]
    H --> I[Dataset estructurado]

    I --> J[Modelo IA]
    J --> K[Score de burnout]
    K --> L[Clasificación de riesgo]

    L --> M[Guardar en Resultados]
    M --> N{¿Riesgo alto?}

    N -- Sí --> O[Generar alerta]
    N -- No --> P[Sin alerta]

    O --> Q[Dashboard]
    P --> Q

    Q --> R[RRHH revisa resultados]
    R --> S[Validación humana]
    S --> T[Intervención organizacional]

    T --> U[Registro de intervención]
    U --> V[Retroalimentación del sistema]
```

# Diagrama de Secuencia (interacción entre componentes)
Se aprecia cada capa durante el proceso
```mermaid
sequenceDiagram
    participant Trabajador
    participant Frontend
    participant Backend
    participant BD
    participant IA

    Trabajador->>Frontend: Responder encuesta
    Frontend->>Backend: Enviar respuestas
    Backend->>BD: Guardar resultados

    Backend->>BD: Consultar datos
    Backend->>IA: Enviar dataset
    IA-->>Backend: Score + riesgo

    Backend->>BD: Guardar análisis

    Backend-->>Frontend: Enviar resultados
    Frontend-->>Trabajador: Mostrar nivel de riesgo
```
# Diagrama de Arquitectura
Diagrama de alto nivel (sin detallar mucho)
```mermaid
flowchart LR
    A[Frontend] --> B[Backend API]
    B --> C[Base de Datos]

    B --> D[Servicio IA]

    D --> B

    B --> E[Motor de Alertas]
    E --> B

    B --> F[Dashboard]

    C --> D
```
# Diagrama de flujo de datos
```mermaid
flowchart TD
    A[Encuestas] --> B[Datos crudos]
    B --> C[Preprocesamiento]
    C --> D[Features]

    D --> E[Modelo IA]
    E --> F[Predicción]

    F --> G[Tabla Análisis]
    G --> H[Dashboard]

    H --> I[Decisiones RRHH]
```

# Diagrama de estado
Ciclo de vida de una encuesta
```mermaid
stateDiagram-v2
    [*] --> Creada
    Creada --> Avalada
    Avalada --> Activa
    Activa --> Cerrada
    Cerrada --> Analizada
    Analizada --> [*]
```
# Diagrama de caso de uso simplificado
```mermaid
flowchart LR
    Trabajador -->|Responde| Sistema
    Sistema -->|Entrega resultado| Trabajador

    RRHH -->|Crea encuestas| Sistema
    RRHH -->|Valida alertas| Sistema
    RRHH -->|Analiza dashboard| Sistema

    Lider -->|Consulta equipo| Sistema

    Sistema -->|Genera predicciones| IA
```
# Diagrama de flujo de aplicación con componentes
```mermaid
flowchart TD
 subgraph RH["👤 Recursos Humanos"]
        A([Inicio]) --> B["Crear encuesta mensual (normal + adicional flaggeados)"]
        B --> C{¿Aprueba la encuesta?}
        C -- No --> B
        C -- Sí --> D["🚩 Flaggear trabajadores en riesgo del período"]
        Z1["Recibir dashboard con resultados individuales"]
        Z2["Recibir reporte grupal consolidado por área"]
        Z3([Fin]) 
  end

  subgraph LID["🧑‍💼 Líder de Equipo"]
        E["Revisar encuesta"]
        Q1["Recibir reporte de su equipo"]
        Q1 --> Z2
  end

  subgraph TRA["👷 Trabajador de Equipo"]
        H["Recibir notificación y acceder a la encuesta"]
        I["Responder encuesta mensual normal"]
        I --> J{¿Fue flaggeado por el líder?}
        J -- Sí --> K["Responder sección adicional de la encuesta"]
        RES["Recibir resultado individual"]
        RES --> Z1
  end

  subgraph SIS["🖥️ Sistema Organizacional"]
        F["Registrar flags. Activar encuesta normal + sección adicional para flaggeados"]
        G["Notificar a trabajadores que la encuesta está disponible"]
        L["Recibir y almacenar respuestas del trabajador"]
        M{¿Todos respondieron o venció el plazo?}
        M -- No --> L
        M -- Sí --> N["Consolidar respuestas y flags. Enviar datos a la IA"]
        P1["Generar reporte personal para cada trabajador"]
        P2["Generar reporte por grupo de trabajo"]
        P3["Tomar contenido de IA y convertirlo en informe"]
        P3 --> Z3
  end

  subgraph IA["🤖 IA"]
        O1["Analizar datos individuales de cada trabajador"]
        O2["Calcular nivel de riesgo individual"]
        O3["Analizar datos grupales por área/equipo"]
        O4["Detectar tendencias comparando con períodos anteriores"]
        O5["Generar el contenido del informe"]
  end

  %% Flujo entre actores
  B --> E
  C -- Sí --> F
  D --> F
  F --> G
  G --> H
  H --> I
  J -- No --> L
  K --> L
  L --> M
  N --> O1
  O1 --> O2 --> O3 --> O4
  O4 --> P1
  P1 --> RES
  O4 --> P2
  P2 --> Q1
  O4 --> O5
  O5 --> P3
  Z2 --> Z3

  %% Estilos por actor
  classDef rh fill:#1a6b6b,stroke:#0d4040,color:#ffffff
  classDef lider fill:#2e8b57,stroke:#1a5c38,color:#ffffff
  classDef trab fill:#3a7ca5,stroke:#1e4d6b,color:#ffffff
  classDef sis fill:#5b5ea6,stroke:#35386b,color:#ffffff
  classDef ia fill:#8b4513,stroke:#5c2d0a,color:#ffffff
  classDef decision fill:#f0a500,stroke:#b07800,color:#000000

  class A,B,D,Z1,Z2,Z3,SO1 rh
  class E,Q1 lider
  class H,I,K,L2,RES trab
  class F,G,L,M,N,P1,P2,P3 sis
  class O1,O2,O3,O4,O5 ia
  class C,J decision
```

