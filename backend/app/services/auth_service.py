# TODO: implement AuthService
# Responsabilidades:
#   - verify_google_token(id_token) → dict con email, name, google_id, avatar_url
#   - get_or_create_google_user(db, google_payload) → User
#   - register_with_password(db, email, password, full_name) → User (status=pending)
#   - authenticate_password(db, email, password) → User | None
#   - create_access_token(user) → str (JWT)
#   - get_current_user(token, db) → User (dependency FastAPI)
#   - require_admin(current_user) → User (dependency FastAPI, lanza 403 si no es admin)
