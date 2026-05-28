# TODO: implement AuditService
# Responsabilidades:
#   - log(db, user_id, action, entity_type, entity_id, changes, ip_address) → AuditLog
#
# Acciones válidas: create | update | delete | status_change | derive | approve | deactivate | login
#
# Llamar al final de toda operación mutante en todos los services.
# Esta función NO hace commit — el commit lo hace el service que la llama.
