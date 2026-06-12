import { describe, it, expect } from 'vitest'
import { calcSeverityPreview, SEVERITY_MATRIX } from '../../utils/severityCalc'

// La fórmula canónica vive en backend/app/services/severity_calculator.py
// (ver .claude/skills/severity-calculator.md). El preview del frontend debe
// producir exactamente los mismos valores que el backend.
describe('calcSeverityPreview', () => {
  describe('exposición (probabilidad × impacto)', () => {
    it.each([
      // [probability, impact, exposure esperada según la matriz canónica]
      ['muy_alta', 'muy_alto', 0.72],
      ['muy_alta', 'alto', 0.36],
      ['muy_alta', 'medio', 0.18],
      ['muy_alta', 'bajo', 0.09],
      ['alta', 'muy_alto', 0.56],
      ['alta', 'alto', 0.28],
      ['alta', 'bajo', 0.07],
      ['media', 'muy_alto', 0.4],
      ['media', 'medio', 0.1],
      ['baja', 'alto', 0.12],
      ['baja', 'bajo', 0.03],
      ['muy_baja', 'muy_bajo', 0.0056],
    ])('%s × %s → %f', (probability, impact, expected) => {
      const result = calcSeverityPreview(probability, impact, 'corto_plazo')
      expect(result.exposure).toBeCloseTo(expected, 4)
    })
  })

  describe('zona y severidad', () => {
    it('muy_alta × bajo (0.09) cae en zona bajo → corto_plazo = 5', () => {
      const result = calcSeverityPreview('muy_alta', 'bajo', 'corto_plazo')
      expect(result.zone).toBe('bajo')
      expect(result.severity).toBe(5)
    })

    it('alta × bajo (0.07) cae en zona bajo → mediano_plazo = 7', () => {
      const result = calcSeverityPreview('alta', 'bajo', 'mediano_plazo')
      expect(result.zone).toBe('bajo')
      expect(result.severity).toBe(7)
    })

    it('baja × muy_alto (0.24) cae en zona medio → corto_plazo = 2', () => {
      const result = calcSeverityPreview('baja', 'muy_alto', 'corto_plazo')
      expect(result.zone).toBe('medio')
      expect(result.severity).toBe(2)
    })

    it('muy_alta × muy_alto (0.72) cae en zona alto → corto_plazo = 1', () => {
      const result = calcSeverityPreview('muy_alta', 'muy_alto', 'corto_plazo')
      expect(result.zone).toBe('alto')
      expect(result.severity).toBe(1)
    })

    it('baja × bajo (0.03) cae en zona bajo → largo_plazo = 9', () => {
      const result = calcSeverityPreview('baja', 'bajo', 'largo_plazo')
      expect(result.zone).toBe('bajo')
      expect(result.severity).toBe(9)
    })
  })

  // El dashboard ubica los issues en la grilla 3×3 por su valor de severidad:
  // eso solo es válido si la matriz es biyectiva (9 celdas → 9 valores únicos).
  it('SEVERITY_MATRIX es biyectiva: 9 valores únicos del 1 al 9', () => {
    const values = Object.values(SEVERITY_MATRIX).flatMap(row => Object.values(row))
    expect([...values].sort((a, b) => a - b)).toEqual([1, 2, 3, 4, 5, 6, 7, 8, 9])
  })

  it('devuelve null si falta algún parámetro', () => {
    expect(calcSeverityPreview('', 'alto', 'corto_plazo')).toBeNull()
    expect(calcSeverityPreview('alta', '', 'corto_plazo')).toBeNull()
    expect(calcSeverityPreview('alta', 'alto', '')).toBeNull()
  })
})
