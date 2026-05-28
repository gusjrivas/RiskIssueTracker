import pytest

from app.schemas.common import ExposureZone, ImpactLevel, Proximity, ProbabilityLevel
from app.services.severity_calculator import get_exposure, get_exposure_zone, get_severity


class TestGetExposure:
    def test_muy_alta_muy_alto_returns_072(self):
        assert get_exposure(ProbabilityLevel.muy_alta, ImpactLevel.muy_alto) == 0.72

    def test_media_medio_returns_010(self):
        assert get_exposure(ProbabilityLevel.media, ImpactLevel.medio) == 0.10

    def test_baja_bajo_returns_003(self):
        assert get_exposure(ProbabilityLevel.baja, ImpactLevel.bajo) == 0.03

    def test_muy_baja_muy_bajo_returns_small_value(self):
        result = get_exposure(ProbabilityLevel.muy_baja, ImpactLevel.muy_bajo)
        assert result < 0.09  # debe caer en zona bajo

    @pytest.mark.parametrize("prob,impact,expected", [
        (ProbabilityLevel.muy_alta, ImpactLevel.muy_alto,  0.72),
        (ProbabilityLevel.muy_alta, ImpactLevel.alto,      0.36),
        (ProbabilityLevel.muy_alta, ImpactLevel.medio,     0.18),
        (ProbabilityLevel.muy_alta, ImpactLevel.bajo,      0.09),
        (ProbabilityLevel.alta,     ImpactLevel.muy_alto,  0.56),
        (ProbabilityLevel.alta,     ImpactLevel.alto,      0.28),
        (ProbabilityLevel.media,    ImpactLevel.muy_alto,  0.40),
        (ProbabilityLevel.media,    ImpactLevel.medio,     0.10),
        (ProbabilityLevel.baja,     ImpactLevel.alto,      0.12),
        (ProbabilityLevel.baja,     ImpactLevel.bajo,      0.03),
    ])
    def test_matrix_values(self, prob, impact, expected):
        assert get_exposure(prob, impact) == expected


class TestGetExposureZone:
    def test_zone_bajo_at_lower_boundary(self):
        assert get_exposure_zone(0.01) == ExposureZone.bajo

    def test_zone_bajo_at_upper_boundary(self):
        assert get_exposure_zone(0.09) == ExposureZone.bajo

    def test_zone_medio_at_lower_boundary(self):
        assert get_exposure_zone(0.10) == ExposureZone.medio

    def test_zone_medio_at_upper_boundary(self):
        assert get_exposure_zone(0.24) == ExposureZone.medio

    def test_zone_alto_at_lower_boundary(self):
        assert get_exposure_zone(0.28) == ExposureZone.alto

    def test_zone_alto_at_upper_boundary(self):
        assert get_exposure_zone(0.72) == ExposureZone.alto

    @pytest.mark.parametrize("exposure,expected_zone", [
        (0.01, ExposureZone.bajo),
        (0.09, ExposureZone.bajo),
        (0.10, ExposureZone.medio),
        (0.20, ExposureZone.medio),
        (0.24, ExposureZone.medio),
        (0.28, ExposureZone.alto),
        (0.36, ExposureZone.alto),
        (0.72, ExposureZone.alto),
    ])
    def test_zone_parametrized(self, exposure, expected_zone):
        assert get_exposure_zone(exposure) == expected_zone


class TestGetSeverity:
    def test_most_critical_severity_is_1(self):
        # muy_alta × muy_alto = 0.72 → zona alto → corto_plazo → 1
        assert get_severity(ProbabilityLevel.muy_alta, ImpactLevel.muy_alto, Proximity.corto_plazo) == 1

    def test_lowest_severity_is_9(self):
        # baja × bajo = 0.03 → zona bajo → largo_plazo → 9
        assert get_severity(ProbabilityLevel.baja, ImpactLevel.bajo, Proximity.largo_plazo) == 9

    def test_medium_severity_is_4(self):
        # media × medio = 0.10 → zona medio → mediano_plazo → 4
        assert get_severity(ProbabilityLevel.media, ImpactLevel.medio, Proximity.mediano_plazo) == 4

    def test_severity_range_is_1_to_9(self):
        for prob in ProbabilityLevel:
            for impact in ImpactLevel:
                for prox in Proximity:
                    result = get_severity(prob, impact, prox)
                    assert 1 <= result <= 9, f"Severity {result} out of range for {prob},{impact},{prox}"

    @pytest.mark.parametrize("prob,impact,prox,expected", [
        # Zona alto — todos los proximity
        (ProbabilityLevel.muy_alta, ImpactLevel.muy_alto, Proximity.corto_plazo,   1),
        (ProbabilityLevel.muy_alta, ImpactLevel.muy_alto, Proximity.mediano_plazo, 3),
        (ProbabilityLevel.muy_alta, ImpactLevel.muy_alto, Proximity.largo_plazo,   6),
        # Zona medio — todos los proximity
        (ProbabilityLevel.media, ImpactLevel.medio, Proximity.corto_plazo,   2),
        (ProbabilityLevel.media, ImpactLevel.medio, Proximity.mediano_plazo, 4),
        (ProbabilityLevel.media, ImpactLevel.medio, Proximity.largo_plazo,   8),
        # Zona bajo — todos los proximity
        (ProbabilityLevel.baja, ImpactLevel.bajo, Proximity.corto_plazo,   5),
        (ProbabilityLevel.baja, ImpactLevel.bajo, Proximity.mediano_plazo, 7),
        (ProbabilityLevel.baja, ImpactLevel.bajo, Proximity.largo_plazo,   9),
    ])
    def test_full_matrix(self, prob, impact, prox, expected):
        assert get_severity(prob, impact, prox) == expected

    def test_proximity_corto_always_more_critical_than_largo_same_exposure(self):
        # Para el mismo nivel de exposición, corto plazo siempre tiene menor número (más crítico)
        severity_corto = get_severity(ProbabilityLevel.media, ImpactLevel.medio, Proximity.corto_plazo)
        severity_largo = get_severity(ProbabilityLevel.media, ImpactLevel.medio, Proximity.largo_plazo)
        assert severity_corto < severity_largo
