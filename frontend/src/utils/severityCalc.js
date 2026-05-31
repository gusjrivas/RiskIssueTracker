const PROB_WEIGHTS = {
  muy_baja: 0.056, baja: 0.10, media: 0.20, alta: 0.40, muy_alta: 0.80,
}
const IMPACT_WEIGHTS = {
  muy_bajo: 0.10, bajo: 0.30, medio: 0.50, alto: 0.70, muy_alto: 0.90,
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
  const exposure = pw * iw
  const zone = exposureZone(exposure)
  const severity = prox[zone]
  return { exposure: +exposure.toFixed(4), zone, severity }
}
