-- ============================================================
-- SEED DATA — desarrollo local
-- ============================================================

-- Admin user (Google auth)
INSERT INTO users (id, email, full_name, google_id, role, status) VALUES
    ('00000000-0000-0000-0000-000000000001',
     'gustavo.rivas@redb.ee',
     'Gustavo Rivas',
     'google-sub-admin-001',
     'admin',
     'active');

-- Regular user (email/password — hash de 'password123')
INSERT INTO users (id, email, full_name, password_hash, role, status) VALUES
    ('00000000-0000-0000-0000-000000000002',
     'lider@redb.ee',
     'Líder de Proyecto',
     '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TiGniYE6Nd.NumkCmOSm0HJiUVG6',
     'user',
     'active');

-- Pending user
INSERT INTO users (id, email, full_name, google_id, role, status) VALUES
    ('00000000-0000-0000-0000-000000000003',
     'nuevo@redb.ee',
     'Usuario Nuevo',
     'google-sub-pending-003',
     'user',
     'pending');

-- ============================================================
-- PROJECTS
-- ============================================================

INSERT INTO projects (id, name, description, client, owner_id) VALUES
    ('a1000000-0000-0000-0000-000000000001',
     'Portal Corporativo',
     'Rediseño del portal web corporativo.',
     'Acme Corp',
     '00000000-0000-0000-0000-000000000002'),
    ('a1000000-0000-0000-0000-000000000002',
     'Migración Cloud',
     'Migración de infraestructura on-premise a AWS.',
     'TechGlobal SA',
     '00000000-0000-0000-0000-000000000002');

-- ============================================================
-- RISKS
-- ============================================================

-- Risk crítico: muy_alta prob, muy_alto impact, corto_plazo → exposure=0.72, zona=alto, severity=1
INSERT INTO risks (
    id, project_id, owner_id, title, description, root_cause,
    category, probability, impact, proximity,
    exposure, exposure_zone, severity, status,
    mitigation_strategy, contingency_plan, client_notification
) VALUES (
    'b1000000-0000-0000-0000-000000000001',
    'a1000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000002',
    'Dada la falta de respaldo de datos, entonces puede perderse información crítica de usuarios durante la migración',
    'El proceso de migración de la base de datos no tiene un mecanismo de rollback probado.',
    'No se realizaron pruebas de migración en un entorno de staging equivalente a producción.',
    'calendario',
    'muy_alta', 'muy_alto', 'corto_plazo',
    0.7200, 'alto', 1, 'in_progress',
    'Implementar proceso de backup automático antes de cada fase de migración.',
    'Activar rollback y restaurar desde el último backup validado.',
    TRUE
);

-- Risk medio: media prob, medio impact, mediano_plazo → exposure=0.10, zona=medio, severity=4
INSERT INTO risks (
    id, project_id, owner_id, title, description, root_cause,
    category, probability, impact, proximity,
    exposure, exposure_zone, severity, status,
    mitigation_strategy, contingency_plan, client_notification
) VALUES (
    'b1000000-0000-0000-0000-000000000002',
    'a1000000-0000-0000-0000-000000000001',
    '00000000-0000-0000-0000-000000000002',
    'Dado el retraso en entrega de diseños UX, entonces el sprint 3 no puede iniciarse a tiempo',
    'El equipo de UX tiene compromisos paralelos con otros proyectos.',
    'Falta de dedicación exclusiva del equipo de diseño al proyecto.',
    'equipo',
    'media', 'medio', 'mediano_plazo',
    0.1000, 'medio', 4, 'open',
    'Agendar reuniones semanales de seguimiento con el equipo UX.',
    'Iniciar el sprint con las pantallas disponibles y agregar las pendientes en iteraciones posteriores.',
    FALSE
);

-- Risk bajo cerrado: baja prob, bajo impact, largo_plazo → exposure=0.03, zona=bajo, severity=9
INSERT INTO risks (
    id, project_id, owner_id, title, description, root_cause,
    category, probability, impact, proximity,
    exposure, exposure_zone, severity, status,
    mitigation_strategy, contingency_plan, client_notification
) VALUES (
    'b1000000-0000-0000-0000-000000000003',
    'a1000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000002',
    'Dada la incompatibilidad de servicios legacy, entonces la migración cloud puede requerir refactoring adicional',
    'Algunos servicios usan protocolos no soportados por AWS natively.',
    'Deuda técnica acumulada en servicios de más de 5 años de antigüedad.',
    'desarrollo',
    'baja', 'bajo', 'largo_plazo',
    0.0300, 'bajo', 9, 'closed',
    'Mapear todos los servicios legacy y evaluar compatibilidad con AWS antes de iniciar.',
    'Usar capa de adaptadores para servicios incompatibles.',
    FALSE
);

-- ============================================================
-- HISTORY ENTRIES
-- ============================================================

INSERT INTO history_entries (entity_type, entity_id, from_status, to_status, changed_by, notes) VALUES
    ('risk', 'b1000000-0000-0000-0000-000000000001',
     'open', 'in_progress',
     '00000000-0000-0000-0000-000000000002',
     'Se asignó al equipo de infraestructura para seguimiento inmediato.'),
    ('risk', 'b1000000-0000-0000-0000-000000000003',
     'open', 'in_progress',
     '00000000-0000-0000-0000-000000000002',
     'Análisis de compatibilidad iniciado.'),
    ('risk', 'b1000000-0000-0000-0000-000000000003',
     'in_progress', 'closed',
     '00000000-0000-0000-0000-000000000002',
     'Se implementó capa de adaptadores. Riesgo mitigado exitosamente.');

-- ============================================================
-- AUDIT LOG
-- ============================================================

INSERT INTO audit_log (user_id, action, entity_type, entity_id, changes) VALUES
    ('00000000-0000-0000-0000-000000000002', 'create', 'risk',
     'b1000000-0000-0000-0000-000000000001', '{"title": {"before": null, "after": "Dada la falta de respaldo..."}}'),
    ('00000000-0000-0000-0000-000000000002', 'status_change', 'risk',
     'b1000000-0000-0000-0000-000000000001', '{"status": {"before": "open", "after": "in_progress"}}');
