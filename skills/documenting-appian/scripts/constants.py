"""
Shared constants for the Appian Process Model → Mermaid generator.
"""
import os

# Base directory used for output and linking
DEFAULT_OUTPUT_DIR = os.path.join('docs', 'process-models')

SHAPE_DEFAULT = 'rect'

# Fallback shape-to-class mapping (used only when detect_shape doesn't return a class)
SHAPE_TO_CLASS = {
    'sm-circ': 'startEvent',
    'dbl-circ': 'endEvent',
    'diamond': 'gateway',
    'fr-rect': 'subprocess',
    'cyl': 'dataStore',
    'rounded': 'userTask',
    'rect': 'scriptTask',
}

# BPMN 2.0 inspired 9-color palette
CLASS_DEFS = """  classDef startEvent fill:#4CAF50,stroke:#2E7D32,color:#fff,stroke-width:2px
  classDef endEvent fill:#F44336,stroke:#C62828,color:#fff,stroke-width:2px
  classDef timerEvent fill:#FFC107,stroke:#F57F17,color:#333,stroke-width:2px
  classDef gateway fill:#FF9800,stroke:#E65100,color:#fff,stroke-width:2px
  classDef subprocess fill:#1565C0,stroke:#0D47A1,color:#fff,stroke-width:2px
  classDef userTask fill:#2D9CDB,stroke:#1A7AB5,color:#fff,stroke-width:1px
  classDef serviceTask fill:#F2994A,stroke:#D4782E,color:#fff,stroke-width:1px
  classDef scriptTask fill:#E0E0E0,stroke:#9E9E9E,color:#333,stroke-width:1px
  classDef sendTask fill:#F06292,stroke:#C2185B,color:#fff,stroke-width:1px
  classDef dataStore fill:#BB6BD9,stroke:#9544B5,color:#fff,stroke-width:1px"""

# Legend items: css_class -> (shape, human label)
LEGEND_ITEMS = {
    'startEvent':  ('sm-circ',  'Start Event'),
    'endEvent':    ('dbl-circ', 'End Event'),
    'timerEvent':  ('sm-circ',  'Timer / Message'),
    'gateway':     ('diamond',  'Gateway'),
    'subprocess':  ('fr-rect',  'Subprocess'),
    'userTask':    ('rounded',  'User Task'),
    'serviceTask': ('rect',     'Service Task'),
    'scriptTask':  ('rect',     'Script Task'),
    'sendTask':    ('rect',     'Send Task'),
    'dataStore':   ('cyl',      'Data Store'),
}

INVALID_WIN_CHARS = set('<>:"/\\|?*')
