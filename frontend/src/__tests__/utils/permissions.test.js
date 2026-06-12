import { describe, it, expect } from 'vitest'
import { canModifyEntity } from '../../utils/permissions'

// Refleja la regla del backend (risk_service/issue_service):
// solo creador, responsable asignado o admin pueden modificar.
describe('canModifyEntity', () => {
  const entity = { created_by: 'user-1', owner_id: 'user-2' }

  it('el admin siempre puede modificar', () => {
    expect(canModifyEntity({ id: 'user-99', role: 'admin' }, entity)).toBe(true)
  })

  it('el creador puede modificar', () => {
    expect(canModifyEntity({ id: 'user-1', role: 'user' }, entity)).toBe(true)
  })

  it('el responsable asignado puede modificar', () => {
    expect(canModifyEntity({ id: 'user-2', role: 'user' }, entity)).toBe(true)
  })

  it('un usuario ajeno no puede modificar', () => {
    expect(canModifyEntity({ id: 'user-3', role: 'user' }, entity)).toBe(false)
  })

  it('sin owner asignado, solo creador o admin', () => {
    const sinOwner = { created_by: 'user-1', owner_id: null }
    expect(canModifyEntity({ id: 'user-2', role: 'user' }, sinOwner)).toBe(false)
    expect(canModifyEntity({ id: 'user-1', role: 'user' }, sinOwner)).toBe(true)
  })

  it('devuelve false si falta user o entity', () => {
    expect(canModifyEntity(null, entity)).toBe(false)
    expect(canModifyEntity({ id: 'user-1', role: 'user' }, null)).toBe(false)
  })
})
