// Debe coincidir con backend/app/services/severity_calculator.py
const PROB_WEIGHTS = {
  muy_baja: 0.10, baja: 0.30, media: 0.50, alta: 0.70, muy_alta: 0.90,
}
const IMPACT_WEIGHTS = {
  muy_bajo: 0.056, bajo: 0.10, medio: 0.20, alto: 0.40, muy_alto: 0.80,
}
const SEVERITY_MATRIX = {
  corto_plazo:    { bajo: 5, medio: 2, alto: 1 },
  mediano_plazo:  { bajo: 7, medio: 4, alto: 3 },
  largo_plazo:    { bajo: 9, medio: 8, alto: 6 },
}

function exposureZone(exposure) {
  if (exposure <= 0.09) return 'bajo'
  if (exposure <= 0.24) return 'medio'
  return 'alto'
}

export function calcSeverityPreview(probability, impact, proximity) {
  const pw = PROB_WEIGHTS[probability]
  const iw = IMPACT_WEIGHTS[impact]
  const prox = SEVERITY_MATRIX[proximity]
  if (!pw || !iw || !prox) return null
  // Redondear antes de clasificar la zona, igual que el backend
  // (round(x, 4)); si no, 0.90 × 0.10 = 0.09000000000000001 cae en
  // zona medio en vez de bajo por error de punto flotante.
  const exposure = +(pw * iw).toFixed(4)
  const zone = exposureZone(exposure)
  const severity = prox[zone]
  return { exposure, zone, severity }
}
