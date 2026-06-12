// Refleja la regla de permisos del backend (risk_service/issue_service):
// solo el creador, el responsable asignado o un admin pueden modificar.
export function canModifyEntity(user, entity) {
  if (!user || !entity) return false
  return user.role === 'admin' || entity.created_by === user.id || entity.owner_id === user.id
}
