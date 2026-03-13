--liquibase formatted sql
--changeset {{FILENAME}}:{{AUTHOR}}{{CONTEXT_CLAUSE}}

-- NOTE: If {{ID_PROCESS}} or {{DNS}} or {{USER}} remain as placeholders, replace them before running Liquibase.

-- Insert process (idempotent)
INSERT INTO process_paas."pr_paas_process"
("pr_entity", "id_process", "pr_name", "pr_description", "pr_owner", "pr_group", "is_reusable", "pr_end_dt", "pr_start_ts", "pr_creation_user", "pr_modification_ts", "pr_modification_user")
SELECT '{{ENTITY}}', {{ID_PROCESS}}, '{{PROCESS_NAME}}', '{{DESCRIPTION}}', '{{OWNER}}', '{{GROUP}}', false, '9999-12-31 00:00:00', now(), '{{USER}}', now(), '{{USER}}'
WHERE NOT EXISTS (
  SELECT 1 FROM process_paas."pr_paas_process"
  WHERE "pr_entity"='{{ENTITY}}' AND "id_process"={{ID_PROCESS}}
);

-- Map process to BPMN definition (idempotent)
INSERT INTO process_paas."pr_paas_process_definition"
("process_id", "pr_entity", "process_definition_id", "pr_start_ts", "pr_creation_user", "pr_modification_ts", "pr_modification_user")
SELECT {{ID_PROCESS}}, '{{ENTITY}}', '{{PROCESS_DEFINITION_ID}}', now(), '{{USER}}', NULL, NULL
WHERE NOT EXISTS (
  SELECT 1 FROM process_paas."pr_paas_process_definition"
  WHERE "process_id"={{ID_PROCESS}} AND "pr_entity"='{{ENTITY}}' AND "process_definition_id"='{{PROCESS_DEFINITION_ID}}'
);

-- Link process and access point (idempotent)
INSERT INTO process_paas."pr_paas_process_access_point"
("pr_entity", "id_process", "id_access_point", "pr_end_dt", "pr_start_ts", "pr_creation_user", "pr_modification_ts", "pr_modification_user")
SELECT '{{ENTITY}}', {{ID_PROCESS}}, {{ACCESS_POINT_ID}}, '9999-12-31 00:00:00', now(), '{{USER}}', NULL, NULL
WHERE NOT EXISTS (
  SELECT 1 FROM process_paas."pr_paas_process_access_point"
  WHERE "pr_entity"='{{ENTITY}}' AND "id_process"={{ID_PROCESS}} AND "id_access_point"={{ACCESS_POINT_ID}}
);

-- Insert process statuses (idempotent)
{{STATUSES_BLOCK}}

-- Insert process stages (idempotent)
INSERT INTO process_paas.pr_paas_process_stage
(id_process, id_stage, pr_end_dt, pr_modification_ts, pr_start_ts, pr_creation_user, pr_entity, pr_modification_user, pr_stage_description, pr_stage_name)
SELECT {{ID_PROCESS}}, 0, '9999-12-31 00:00:00.000', NULL, now(), '{{USER}}', '{{ENTITY}}', NULL, NULL, NULL
WHERE NOT EXISTS (
  SELECT 1 FROM process_paas.pr_paas_process_stage
  WHERE pr_entity='{{ENTITY}}' AND id_process={{ID_PROCESS}} AND id_stage=0
);

INSERT INTO process_paas.pr_paas_process_stage
(id_process, id_stage, pr_end_dt, pr_modification_ts, pr_start_ts, pr_creation_user, pr_entity, pr_modification_user, pr_stage_description, pr_stage_name)
SELECT {{ID_PROCESS}}, 1, '9999-12-31 00:00:00.000', NULL, now(), '{{USER}}', '{{ENTITY}}', NULL, NULL, NULL
WHERE NOT EXISTS (
  SELECT 1 FROM process_paas.pr_paas_process_stage
  WHERE pr_entity='{{ENTITY}}' AND id_process={{ID_PROCESS}} AND id_stage=1
);

-- Insert process task (idempotent)
INSERT INTO process_paas."pr_paas_process_task"
("pr_entity", "id_process", "id_task", "pr_task_name", "pr_task_description", "pr_task_link", "type_task", "pr_end_dt", "pr_start_ts", "pr_creation_user", "pr_modification_ts", "pr_modification_user")
SELECT '{{ENTITY}}', {{ID_PROCESS}}, 1, 'Manual Task', '...', '', 1, '9999-12-31 00:00:00', now(), '{{USER}}', NULL, NULL
WHERE NOT EXISTS (
  SELECT 1 FROM process_paas."pr_paas_process_task"
  WHERE "pr_entity"='{{ENTITY}}' AND "id_process"={{ID_PROCESS}} AND "id_task"=1
);

-- Insert task actions (idempotent)
INSERT INTO process_paas."pr_paas_task_action"
("pr_entity", "id_process", "id_action", "pr_action_name", "pr_action_description", "id_task", "id_access_point", "id_group", "pr_end_dt", "pr_start_ts", "pr_creation_user", "pr_modification_ts", "pr_modification_user")
SELECT '{{ENTITY}}', {{ID_PROCESS}}, 1, 'Complete', 'Complete task', 1, {{ACCESS_POINT_ID}}, NULL, '9999-12-31 00:00:00', now(), '{{USER}}', NULL, NULL
WHERE NOT EXISTS (
  SELECT 1 FROM process_paas."pr_paas_task_action"
  WHERE "pr_entity"='{{ENTITY}}' AND "id_process"={{ID_PROCESS}} AND "id_action"=1
);

INSERT INTO process_paas."pr_paas_task_action"
("pr_entity", "id_process", "id_action", "pr_action_name", "pr_action_description", "id_task", "id_access_point", "id_group", "pr_end_dt", "pr_start_ts", "pr_creation_user", "pr_modification_ts", "pr_modification_user")
SELECT '{{ENTITY}}', {{ID_PROCESS}}, 2, 'Cancel', 'Cancel task', 1, {{ACCESS_POINT_ID}}, NULL, '9999-12-31 00:00:00', now(), '{{USER}}', NULL, NULL
WHERE NOT EXISTS (
  SELECT 1 FROM process_paas."pr_paas_task_action"
  WHERE "pr_entity"='{{ENTITY}}' AND "id_process"={{ID_PROCESS}} AND "id_action"=2
);

-- Insert process management (idempotent)
INSERT INTO process_paas."pr_paas_process_management"
("id_process", "pr_entity", "dns", "pr_realm", "pr_start_ts", "pr_creation_user", "pr_modification_ts", "pr_modification_user")
SELECT {{ID_PROCESS}}, '{{ENTITY}}', '{{DNS}}', '{{REALM}}', now(), '{{USER}}', now(), '{{USER}}'
WHERE NOT EXISTS (
  SELECT 1 FROM process_paas."pr_paas_process_management"
  WHERE "id_process"={{ID_PROCESS}} AND "pr_entity"='{{ENTITY}}' AND "dns"='{{DNS}}'
);

-- Insert process event (idempotent)
INSERT INTO process_paas.pr_paas_process_event
(pr_entity, id_process, id_event, pr_event_name, pr_event_description, pr_origin_app, pr_end_dt, pr_start_ts, pr_creation_user, pr_modification_ts, pr_modification_user)
SELECT '{{ENTITY}}', {{ID_PROCESS}}, 1, 'cancel', 'Cancel Manual task event', '{{ORIGIN_APP}}', '9999-12-31 00:00:00.000', now(), '{{USER}}', NULL, NULL
WHERE NOT EXISTS (
  SELECT 1 FROM process_paas.pr_paas_process_event
  WHERE pr_entity='{{ENTITY}}' AND id_process={{ID_PROCESS}} AND id_event=1
);

COMMIT;

-- Rollback
--rollback DELETE FROM process_paas.pr_paas_process_event WHERE pr_entity='{{ENTITY}}' AND id_process={{ID_PROCESS}} AND id_event=1;
--rollback DELETE FROM process_paas."pr_paas_process_management" WHERE id_process={{ID_PROCESS}} AND pr_entity='{{ENTITY}}' AND dns='{{DNS}}';
--rollback DELETE FROM process_paas."pr_paas_task_action" WHERE pr_entity='{{ENTITY}}' AND id_process={{ID_PROCESS}} AND id_action IN (1,2);
--rollback DELETE FROM process_paas."pr_paas_process_task" WHERE pr_entity='{{ENTITY}}' AND id_process={{ID_PROCESS}} AND id_task=1;
--rollback DELETE FROM process_paas.pr_paas_process_stage WHERE pr_entity='{{ENTITY}}' AND id_process={{ID_PROCESS}} AND id_stage IN (0,1);
{{STATUSES_ROLLBACK_BLOCK}}
--rollback DELETE FROM process_paas."pr_paas_process_access_point" WHERE pr_entity='{{ENTITY}}' AND id_process={{ID_PROCESS}} AND id_access_point={{ACCESS_POINT_ID}};
--rollback DELETE FROM process_paas."pr_paas_process_definition" WHERE process_id={{ID_PROCESS}} AND pr_entity='{{ENTITY}}' AND process_definition_id='{{PROCESS_DEFINITION_ID}}';
--rollback DELETE FROM process_paas."pr_paas_process" WHERE pr_entity='{{ENTITY}}' AND id_process={{ID_PROCESS}};
--rollback COMMIT;
