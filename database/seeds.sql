-- Seed data for development

-- Projects
INSERT INTO projects (id, name, description, client) VALUES
    ('a1b2c3d4-0001-0001-0001-000000000001', 'Portal Corporativo', 'Rediseño del portal web corporativo', 'Acme Corp'),
    ('a1b2c3d4-0002-0002-0002-000000000002', 'Migración Cloud', 'Migración de infraestructura on-premise a AWS', 'TechGlobal SA');

-- Risks for Project 1
INSERT INTO risks (id, project_id, title, description, probability, impact, urgency, scope, severity, status) VALUES
    (
        'b1b2c3d4-0001-0001-0001-000000000001',
        'a1b2c3d4-0001-0001-0001-000000000001',
        'Pérdida de datos de usuarios',
        'Riesgo de pérdida de datos durante la migración de la base de datos del portal.',
        4, 5, 3, 3,
        'critical',
        'open'
    ),
    (
        'b1b2c3d4-0002-0002-0002-000000000002',
        'a1b2c3d4-0001-0001-0001-000000000001',
        'Retraso en entrega de diseños',
        'El equipo de UX podría no entregar los mockups a tiempo para el sprint 3.',
        3, 3, 2, 2,
        'medium',
        'in_progress'
    );

-- Risk for Project 2
INSERT INTO risks (id, project_id, title, description, probability, impact, urgency, scope, severity, status) VALUES
    (
        'b1b2c3d4-0003-0003-0003-000000000003',
        'a1b2c3d4-0002-0002-0002-000000000002',
        'Incompatibilidad de servicios legacy',
        'Algunos servicios legacy podrían no ser compatibles con la nueva arquitectura AWS.',
        2, 4, 1, 2,
        'medium',
        'closed'
    );

-- History entries for the risks
INSERT INTO history_entries (entity_type, entity_id, from_status, to_status, changed_by, notes) VALUES
    ('risk', 'b1b2c3d4-0002-0002-0002-000000000002', 'open', 'in_progress', 'gustavo.rivas@redb.ee', 'Se asignó al equipo de diseño para seguimiento.'),
    ('risk', 'b1b2c3d4-0003-0003-0003-000000000003', 'open', 'in_progress', 'gustavo.rivas@redb.ee', 'Análisis de compatibilidad iniciado.'),
    ('risk', 'b1b2c3d4-0003-0003-0003-000000000003', 'in_progress', 'closed', 'gustavo.rivas@redb.ee', 'Se implementó capa de adaptadores. Riesgo mitigado.');
