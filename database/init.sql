-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- ENUM TYPES
-- ============================================================

CREATE TYPE risk_status AS ENUM ('open', 'in_progress', 'closed', 'derived');
CREATE TYPE issue_status AS ENUM ('open', 'in_progress', 'closed');
CREATE TYPE probability_level AS ENUM ('muy_baja', 'baja', 'media', 'alta', 'muy_alta');
CREATE TYPE impact_level AS ENUM ('muy_bajo', 'bajo', 'medio', 'alto', 'muy_alto');
CREATE TYPE proximity AS ENUM ('corto_plazo', 'mediano_plazo', 'largo_plazo');
CREATE TYPE exposure_zone AS ENUM ('bajo', 'medio', 'alto');
CREATE TYPE risk_category AS ENUM ('calendario', 'alcance', 'ingresos', 'costos', 'presupuesto', 'equipo', 'gestion');
CREATE TYPE user_role AS ENUM ('admin', 'user');
CREATE TYPE user_status AS ENUM ('pending', 'active', 'inactive');
CREATE TYPE entity_type AS ENUM ('risk', 'issue', 'project', 'user');

-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email         VARCHAR(255) NOT NULL UNIQUE,
    full_name     VARCHAR(255) NOT NULL,
    google_id     VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    avatar_url    VARCHAR(500),
    role          user_role NOT NULL DEFAULT 'user',
    status        user_status NOT NULL DEFAULT 'pending',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_users_auth CHECK (google_id IS NOT NULL OR password_hash IS NOT NULL)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_google_id ON users(google_id);
CREATE INDEX idx_users_status ON users(status);

-- ============================================================
-- PROJECTS
-- ============================================================

CREATE TABLE projects (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    client      VARCHAR(255),
    owner_id    UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_projects_owner_id ON projects(owner_id);

-- ============================================================
-- RISKS
-- ============================================================

CREATE TABLE risks (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    owner_id            UUID REFERENCES users(id) ON DELETE SET NULL,
    title               VARCHAR(500) NOT NULL,
    description         TEXT,
    root_cause          TEXT,
    application_team    VARCHAR(255),
    category            risk_category,
    probability         probability_level NOT NULL,
    impact              impact_level NOT NULL,
    proximity           proximity NOT NULL,
    exposure            NUMERIC(6,4) NOT NULL,
    exposure_zone       exposure_zone NOT NULL,
    severity            SMALLINT NOT NULL CHECK (severity BETWEEN 1 AND 9),
    status              risk_status NOT NULL DEFAULT 'open',
    mitigation_strategy TEXT,
    contingency_plan    TEXT,
    client_notification BOOLEAN NOT NULL DEFAULT FALSE,
    derived_issue_id    UUID,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_risks_project_id ON risks(project_id);
CREATE INDEX idx_risks_owner_id ON risks(owner_id);
CREATE INDEX idx_risks_status ON risks(status);
CREATE INDEX idx_risks_severity ON risks(severity);
CREATE INDEX idx_risks_category ON risks(category);
CREATE INDEX idx_risks_proximity ON risks(proximity);

-- ============================================================
-- ISSUES
-- ============================================================

CREATE TABLE issues (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    risk_id             UUID REFERENCES risks(id) ON DELETE SET NULL,
    owner_id            UUID REFERENCES users(id) ON DELETE SET NULL,
    title               VARCHAR(500) NOT NULL,
    description         TEXT,
    severity            SMALLINT NOT NULL CHECK (severity BETWEEN 1 AND 9),
    status              issue_status NOT NULL DEFAULT 'open',
    mitigation_strategy TEXT,
    contingency_plan    TEXT,
    client_notification BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_issues_project_id ON issues(project_id);
CREATE INDEX idx_issues_risk_id ON issues(risk_id);
CREATE INDEX idx_issues_owner_id ON issues(owner_id);
CREATE INDEX idx_issues_status ON issues(status);
CREATE INDEX idx_issues_severity ON issues(severity);

-- FK diferida para evitar dependencia circular risks ↔ issues
ALTER TABLE risks
    ADD CONSTRAINT fk_risks_derived_issue
    FOREIGN KEY (derived_issue_id) REFERENCES issues(id) ON DELETE SET NULL;

CREATE INDEX idx_risks_derived_issue_id ON risks(derived_issue_id);

-- ============================================================
-- HISTORY ENTRIES (append-only, sin FK explícitas)
-- ============================================================

CREATE TABLE history_entries (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type   entity_type NOT NULL,
    entity_id     UUID NOT NULL,
    from_status   VARCHAR(50),
    to_status     VARCHAR(50) NOT NULL,
    changed_by    UUID,
    notes         TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_history_entries_entity ON history_entries(entity_type, entity_id);
CREATE INDEX idx_history_entries_created_at ON history_entries(created_at);

-- ============================================================
-- AUDIT LOG (append-only)
-- ============================================================

CREATE TABLE audit_log (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id       UUID,
    action        VARCHAR(50) NOT NULL,
    entity_type   VARCHAR(50) NOT NULL,
    entity_id     UUID,
    changes       JSONB,
    ip_address    VARCHAR(45),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
