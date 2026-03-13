<!-- DEPRECATED FALLBACK: pm2mermaid.py prefers references/legend.md (full Palette A+B).
     This file is only copied if legend.md is missing. Do NOT edit here — edit legend.md instead. -->
# Leyenda de colores — Diagramas BPMN

Los diagramas de Process Models usan la paleta BPMN 2.0:

| Tipo BPMN | Color | Nodos Appian |
|-----------|-------|-------------|
| **Start Event** | 🟢 Verde (`#4CAF50`) | `core.0` Start Node |
| **End Event** | 🔴 Rojo (`#F44336`) | `core.1` End Node |
| **Timer/Message Event** | 🟡 Amarillo (`#FFC107`) | `core.7` Intermediate Event |
| **Gateway** (AND/XOR/OR) | 🟠 Naranja (`#FF9800`) | `core.2`-`core.5` |
| **Subprocess / Call Activity** | 🔵 Azul oscuro (`#1565C0`) | `internal.38` SUB_PROC, Start Process |
| **User Task** | 🔵 Azul claro (`#2D9CDB`) | `internal.17` User Input Task |
| **Service Task** | 🟠 Naranja claro (`#F2994A`) | Call Integration, SFTP, Kafka, SAP |
| **Script Task** | ⚪ Gris (`#E0E0E0`) | `internal.16` Script Task, otros |
| **Send Task** | 🩷 Rosa (`#F06292`) | Send E-Mail, Push Notification |
| **Data Store ops** | 🟣 Púrpura (`#BB6BD9`) | Write/Delete/Query Data Store |

## Flechas

| Estilo | Significado |
|--------|------------|
| `==>` (gruesa) | Flujo principal (Start → primera actividad → gateway principal) |
| `-->` (normal) | Flujo estándar |
| `-.->` (punteada) | Flujo de error / alternativo / salto a End |
| `-->\|"Si"\|` | Rama positiva de XOR gateway |
| `-->\|"No"\|` | Rama negativa de XOR gateway |

## Subgraphs

Los procesos con más de 30 nodos se agrupan en subgraphs por ramas paralelas (AND gateways).

## Click links

Los nodos de tipo **Subprocess** son clickables y enlazan al diagrama del subproceso correspondiente.
