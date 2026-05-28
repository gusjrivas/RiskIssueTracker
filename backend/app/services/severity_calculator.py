from app.schemas.common import ExposureZone, ImpactLevel, ProbabilityLevel, Proximity

PROBABILITY_WEIGHTS: dict[ProbabilityLevel, float] = {
    ProbabilityLevel.muy_baja: 0.10,
    ProbabilityLevel.baja: 0.30,
    ProbabilityLevel.media: 0.50,
    ProbabilityLevel.alta: 0.70,
    ProbabilityLevel.muy_alta: 0.90,
}

IMPACT_WEIGHTS: dict[ImpactLevel, float] = {
    ImpactLevel.muy_bajo: 0.056,
    ImpactLevel.bajo: 0.10,
    ImpactLevel.medio: 0.20,
    ImpactLevel.alto: 0.40,
    ImpactLevel.muy_alto: 0.80,
}

# Severity matrix: MATRIX[proximity][exposure_zone] → int 1-9 (1 = most critical)
SEVERITY_MATRIX: dict[Proximity, dict[ExposureZone, int]] = {
    Proximity.corto_plazo: {
        ExposureZone.bajo: 5,
        ExposureZone.medio: 2,
        ExposureZone.alto: 1,
    },
    Proximity.mediano_plazo: {
        ExposureZone.bajo: 7,
        ExposureZone.medio: 4,
        ExposureZone.alto: 3,
    },
    Proximity.largo_plazo: {
        ExposureZone.bajo: 9,
        ExposureZone.medio: 8,
        ExposureZone.alto: 6,
    },
}


def get_exposure(probability: ProbabilityLevel, impact: ImpactLevel) -> float:
    return round(PROBABILITY_WEIGHTS[probability] * IMPACT_WEIGHTS[impact], 4)


def get_exposure_zone(exposure: float) -> ExposureZone:
    if exposure <= 0.09:
        return ExposureZone.bajo
    if exposure <= 0.24:
        return ExposureZone.medio
    return ExposureZone.alto


def get_severity(
    probability: ProbabilityLevel,
    impact: ImpactLevel,
    proximity: Proximity,
) -> int:
    exposure = get_exposure(probability, impact)
    zone = get_exposure_zone(exposure)
    return SEVERITY_MATRIX[proximity][zone]
