# TODO: implement AuditLog SQLAlchemy model (append-only)
# Campos:
#   id UUID PK
#   user_id UUID nullable (FK users.id, sin cascade — el log persiste aunque se borre el user)
#   action VARCHAR(50) NOT NULL
#   entity_type VARCHAR(50) NOT NULL
#   entity_id UUID nullable
#   changes JSONB nullable  ({"field": {"before": x, "after": y}})
#   ip_address VARCHAR(45) nullable
#   created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
# Sin updated_at — tabla append-only
