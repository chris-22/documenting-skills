"""
BPMN node classification for Appian Process Model nodes.

Maps Appian ac/local-id patterns to Mermaid shapes and CSS classes.
"""
from typing import Tuple

from xml_helpers import find_child, text, pick_fname
from constants import SHAPE_DEFAULT


def sanitize_label(s: str) -> str:
    """Escape and normalise a label for use inside Mermaid syntax."""
    if not s:
        return ''
    # Escape quotes and special chars per Mermaid docs
    s = s.replace('"', '&quot;')
    # Collapse newlines
    s = ' '.join(s.split())
    return s


def detect_shape(node) -> Tuple[str, str, str]:
    """Return (shape, label, css_class) for a node.

    Classification based on BPMN 2.0 standard + official Appian docs
    (Process Nodes and Smart Services) + verified local-id patterns.

    BPMN mapping -> Mermaid shapes + CSS classes:
      Start Event      -> sm-circ   + startEvent  (green)
      End Event        -> dbl-circ  + endEvent    (red)
      Timer/Message    -> sm-circ   + timerEvent  (yellow)
      Gateways         -> diamond   + gateway     (orange)
      Subprocess/Call  -> fr-rect   + subprocess  (dark blue)
      User Task        -> rounded   + userTask    (light blue)
      Service Task     -> rect      + serviceTask (orange)
      Script Task      -> rect      + scriptTask  (gray)
      Send Task        -> rect      + sendTask    (pink)
      Data Store ops   -> cyl       + dataStore   (purple)
    """
    ac = find_child(node, 'ac')
    ac_local = text(find_child(ac, 'local-id')) if ac is not None else ''
    ac_name = text(find_child(ac, 'name')) if ac is not None else ''
    label = pick_fname(node) or ac_name or ''
    label = sanitize_label(label)
    ac_local_lower = ac_local.lower()
    ac_name_lower = ac_name.lower()
    label_lower = label.lower()

    # --- 1. EVENTS (Start, End, Timer, Message) ---
    if ac_local == 'core.0' or ac_name == 'Start Node':
        return ('sm-circ', label or 'Start Node', 'startEvent')
    if ac_local == 'core.1' or ac_name == 'End Node':
        return ('dbl-circ', label or 'End Node', 'endEvent')
    if ac_local == 'core.7':  # Intermediate Consuming Event (Timer/Receive Message)
        return ('sm-circ', label or 'Event', 'timerEvent')

    # --- 2. GATEWAYS (AND, XOR, OR, Complex) ---
    if ac_local == 'core.2' or ac_name == 'AND':
        return ('diamond', label or 'AND', 'gateway')
    if ac_local == 'core.3' or ac_name == 'OR':
        return ('diamond', label or 'OR', 'gateway')
    if ac_local == 'core.4' or ac_name == 'XOR':
        return ('diamond', label or 'XOR', 'gateway')
    if ac_local == 'core.5' or ac_name == 'Complex':
        return ('diamond', label or 'Complex', 'gateway')

    # --- 3. SUBPROCESS and START PROCESS (BPMN: Subprocess / Call Activity) ---
    if ac_name == 'SUB_PROC' or ac_local == 'internal.38':
        return ('fr-rect', label or 'Subprocess', 'subprocess')
    if 'start-process' in ac_local_lower or 'start process' in ac_name_lower:
        return ('fr-rect', label or 'Start Process', 'subprocess')

    # --- 4. DATA SMART SERVICES -> cylinder (BPMN: Data Store reference) ---
    if 'write-to-data-store' in ac_local_lower or 'multi-write-to-data-store' in ac_local_lower:
        return ('cyl', label or 'Write to Data Store', 'dataStore')
    if 'delete' in ac_local_lower and 'data-store' in ac_local_lower:
        return ('cyl', label or 'Delete from Data Store', 'dataStore')
    if 'data-export-entity' in ac_local_lower:
        return ('cyl', label or 'Export Data Store', 'dataStore')
    if 'storedprocedure' in ac_local_lower or 'stored procedure' in ac_name_lower:
        return ('cyl', label or 'Stored Procedure', 'dataStore')
    if 'query-database' in ac_local_lower or 'query database' in ac_name_lower:
        return ('cyl', label or 'Query Database', 'dataStore')
    if 'write-records' in ac_local_lower or 'delete-records' in ac_local_lower:
        return ('cyl', label or 'Records Operation', 'dataStore')
    if 'sync-records' in ac_local_lower:
        return ('cyl', label or 'Sync Records', 'dataStore')
    if any(kw in label_lower for kw in ('write to', 'escritura bbdd', 'escritura bd', 'delete from')):
        return ('cyl', label, 'dataStore')

    # --- 5. SCRIPT TASK (BPMN: Script Task) -> rect + gray ---
    if ac_local == 'internal.16' or ac_name == 'Unattended Multiple Questions':
        return (SHAPE_DEFAULT, label or 'Script Task', 'scriptTask')

    # --- 6. USER TASK (BPMN: User Task) -> rounded + light blue ---
    if ac_local == 'internal.17' or ac_name == 'User Input Task':
        return ('rounded', label or 'User Task', 'userTask')

    # --- 7. SEND TASK (BPMN: Send Task) -> rect + pink ---
    if ac_name == 'Send E-Mail' or 'sendemail' in ac_local_lower:
        return (SHAPE_DEFAULT, label or 'Send E-Mail', 'sendTask')
    if 'send-push' in ac_local_lower or 'push notification' in ac_name_lower:
        return (SHAPE_DEFAULT, label or 'Send Notification', 'sendTask')

    # --- 8. SERVICE TASK (BPMN: Service Task) -> rect + orange ---
    # Integration calls, SFTP, Kafka, SAP, Call Web Service
    if 'integration' in ac_local_lower or 'integration' in ac_name_lower:
        return (SHAPE_DEFAULT, label or 'Call Integration', 'serviceTask')
    if 'sftp' in ac_local_lower or 'sftp' in ac_name_lower:
        return (SHAPE_DEFAULT, label or 'SFTP', 'serviceTask')
    if 'kafka' in ac_local_lower or 'kafka' in ac_name_lower:
        return (SHAPE_DEFAULT, label or 'Kafka', 'serviceTask')
    if 'web-service' in ac_local_lower or 'web service' in ac_name_lower:
        return (SHAPE_DEFAULT, label or 'Call Web Service', 'serviceTask')
    if 'sap' in ac_local_lower or 'sap' in ac_name_lower:
        return (SHAPE_DEFAULT, label or 'SAP', 'serviceTask')

    # --- 9. ALL OTHER (BPMN: various) -> rect + gray (scriptTask as default) ---
    # Document generation, Excel ops, Group/User management, Cancel/Complete process, etc.
    return (SHAPE_DEFAULT, label or 'Activity', 'scriptTask')
