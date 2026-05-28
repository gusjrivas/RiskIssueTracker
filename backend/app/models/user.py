# TODO: implement User SQLAlchemy model
# Campos:
#   id UUID PK
#   email VARCHAR(255) UNIQUE NOT NULL
#   full_name VARCHAR(255) NOT NULL
#   google_id VARCHAR(255) UNIQUE nullable
#   password_hash VARCHAR(255) nullable
#   avatar_url VARCHAR(500) nullable
#   role user_role NOT NULL DEFAULT 'user'
#   status user_status NOT NULL DEFAULT 'pending'
#   created_at TIMESTAMPTZ
#   updated_at TIMESTAMPTZ
# Constraint: CHECK (google_id IS NOT NULL OR password_hash IS NOT NULL)
