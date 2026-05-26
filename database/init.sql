-- Extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum types
CREATE TYPE risk_status AS ENUM ('open', 'in_progress', 'closed');
CREATE TYPE issue_status AS ENUM ('open', 'in_progress', 'closed');
CREATE TYPE severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE action_status AS ENUM ('pending', 'in_progress', 'done');
CREATE TYPE entity_type AS ENUM ('risk', 'issue');

-- projects
CREATE TABLE projects (
    id          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name        VARCHAR(255) NOT NULL,
    description TEXT,
    client      VARCHAR(255),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- risks
CREATE TABLE risks (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id    UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title         VARCHAR(255) NOT NULL,
    description   TEXT,
    probability   SMALLINT NOT NULL CHECK (probability BETWEEN 1 AND 5),
    impact        SMALLINT NOT NULL CHECK (impact BETWEEN 1 AND 5),
    urgency       SMALLINT NOT NULL CHECK (urgency BETWEEN 1 AND 3),
    scope         SMALLINT NOT NULL CHECK (scope BETWEEN 1 AND 3),
    severity      severity NOT NULL,
    status        risk_status NOT NULL DEFAULT 'open',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_risks_project_id ON risks(project_id);
CREATE INDEX idx_risks_status ON risks(status);
CREATE INDEX idx_risks_severity ON risks(severity);

-- issues
CREATE TABLE issues (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id    UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    risk_id       UUID REFERENCES risks(id) ON DELETE SET NULL,
    title         VARCHAR(255) NOT NULL,
    description   TEXT,
    severity      severity NOT NULL,
    status        issue_status NOT NULL DEFAULT 'open',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_issues_project_id ON issues(project_id);
CREATE INDEX idx_issues_risk_id ON issues(risk_id);
CREATE INDEX idx_issues_status ON issues(status);
CREATE INDEX idx_issues_severity ON issues(severity);

-- mitigation_plans
CREATE TABLE mitigation_plans (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type   entity_type NOT NULL,
    entity_id     UUID NOT NULL,
    title         VARCHAR(255) NOT NULL,
    description   TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_mitigation_plans_entity ON mitigation_plans(entity_type, entity_id);

-- mitigation_actions
CREATE TABLE mitigation_actions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    mitigation_plan_id  UUID NOT NULL REFERENCES mitigation_plans(id) ON DELETE CASCADE,
    title               VARCHAR(255) NOT NULL,
    description         TEXT,
    assignee            VARCHAR(255),
    due_date            DATE,
    status              action_status NOT NULL DEFAULT 'pending',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_mitigation_actions_plan_id ON mitigation_actions(mitigation_plan_id);
CREATE INDEX idx_mitigation_actions_status ON mitigation_actions(status);

-- history_entries (append-only, sin FK explícitas para soportar risk e issue)
CREATE TABLE history_entries (
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    entity_type   entity_type NOT NULL,
    entity_id     UUID NOT NULL,
    from_status   VARCHAR(50),
    to_status     VARCHAR(50) NOT NULL,
    changed_by    VARCHAR(255),
    notes         TEXT,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_history_entries_entity ON history_entries(entity_type, entity_id);
CREATE INDEX idx_history_entries_created_at ON history_entries(created_at);
