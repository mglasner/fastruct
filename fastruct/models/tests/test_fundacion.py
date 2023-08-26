"""Test para el modelo de Fundacion."""
from random import randint
from typing import Literal

import pytest
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Session

from ..foundation import Fundacion
from .fixtures import engine, fundacion_1_1_1, session

# def test_crear_fundacion(session: Session, fundacion_1_1_1: Fundacion):
#     """Crear una instacia en base de datos."""
#     fundaciones = session.query(Fundacion).all()
#     fundacion = fundaciones[0]
#     assert len(fundaciones) == 1
#     assert fundacion.lx == fundacion_1_1_1.lx
#     assert fundacion.ly == fundacion_1_1_1.ly
#     assert fundacion.lz == fundacion_1_1_1.lz
#     assert fundacion.lx == 1
#     assert fundacion.ly == 1
#     assert fundacion.lz == 1


# @pytest.mark.parametrize(
#     "lx,ly,lz",
#     [
#         (0, 1, 1),  # lx es 0
#         (1, 0, 1),  # ly es 0
#         (1, 1, 0),  # lz es 0
#         (-1, 1, 1),  # lx es negativo
#         (1, -1, 1),  # ly es negativo
#         (1, 1, -1),  # lz es negativo
#     ],
# )
# def test_fundacion_invalid_values(session: Session, lx: float, ly: float, lz: float) -> None:
#     """Prueba la creación de instancias de la clase Fundacion con valores numéricos no válidos."""
#     with pytest.raises(IntegrityError):
#         fundacion = Fundacion(lx=lx, ly=ly, lz=lz)
#         session.add(fundacion)
#         session.commit()


# @pytest.mark.parametrize(
#     "lx,ly,lz",
#     [
#         ("a", 1, 1),  # lx es una cadena
#         (1, "b", 1),  # ly es una cadena
#         (1, 1, "c"),  # lz es una cadena
#     ],
# )
# def test_fundacion_invalid_string_values(session: Session, lx: str, ly: str, lz: str) -> None:
#     """Prueba la creación de instancias de la clase Fundacion con valores de cadena."""
#     with pytest.raises(StatementError, match="could not convert string to float"):
#         fundacion = Fundacion(lx=lx, ly=ly, lz=lz)
#         session.add(fundacion)
#         session.commit()


# @pytest.mark.parametrize(
#     "lx, ly, expected_area",
#     [
#         (10.0, 5.0, 50.0),
#         (5.00, 5.0, 25.0),
#         (2.00, 3.0, 6.00),
#     ],
# )
# def test_fundacion_area(lx: float, ly: float, expected_area: float) -> None:
#     """Prueba el cálculo del área de la fundación.

#     Verifica que el cálculo del área sea correcto para varios casos de prueba.

#     Args:
#         lx: Longitud en la dimensión X de la fundación.
#         ly: Longitud en la dimensión Y de la fundación.
#         expected_area: Área esperada para las dimensiones dadas.
#     """
#     fundacion = Fundacion(lx=lx, ly=ly, lz=randint(1, 100))

#     assert fundacion.area() == expected_area


# @pytest.mark.parametrize(
#     "lx, ly, lz, expected_volumen",
#     [
#         (10.0, 5.0, 2.0, 100.0),
#         (5.00, 5.0, 5.0, 125.0),
#         (2.00, 3.0, 4.0, 24.00),
#     ],
# )
# def test_fundacion_volumen(lx: float, ly: float, lz: float, expected_volumen: float) -> None:
#     """Prueba el cálculo del volumen de la fundación.

#     Verifica que el cálculo del volumen sea correcto para varios casos de prueba.

#     Args:
#         lx: Longitud en la dimensión X de la fundación.
#         ly: Longitud en la dimensión Y de la fundación.
#         lz: Longitud en la dimensión Z de la fundación.
#         expected_volumen: Volumen esperado para las dimensiones dadas.
#     """
#     fundacion = Fundacion(lx=lx, ly=ly, lz=lz)

#     assert fundacion.volumen() == expected_volumen


# @pytest.mark.parametrize(
#     "lx, ly, lz, densidad, expected_peso",
#     [
#         (10.0, 5.0, 2.0, 2.5, 250.0),
#         (5.00, 5.0, 5.0, 2.5, 312.5),
#         (2.00, 3.0, 4.0, 3.0, 72.00),
#     ],
# )
# def test_fundacion_peso(lx: float, ly: float, lz: float, densidad: float, expected_peso: float) -> None:
#     """Prueba el cálculo del peso de la fundación.

#     Verifica que el cálculo del peso sea correcto para varios casos de prueba.

#     Args:
#         lx: Longitud en la dimensión X de la fundación.
#         ly: Longitud en la dimensión Y de la fundación.
#         lz: Longitud en la dimensión Z de la fundación.
#         densidad: Densidad de la fundación en Ton/m³.
#         expected_peso: Peso esperado para las dimensiones y densidad dadas.
#     """
#     fundacion = Fundacion(lx=lx, ly=ly, lz=lz)

#     assert fundacion.peso(densidad) == expected_peso


@pytest.mark.parametrize(
    "lx, ly, axial, momento, direccion, expected_result",
    [
        # ----- ZAPATA ACHICANDOSE X (Lx)--
        (5.0, 5.0, 10.00, 5.00, "x", True),
        (4.5, 5.0, 10.00, 5.00, "x", True),
        (4.0, 5.0, 10.00, 5.00, "x", True),
        (3.5, 5.0, 10.00, 5.00, "x", True),
        (3.0, 5.0, 10.00, 5.00, "x", True),
        (2.5, 5.0, 10.00, 5.00, "x", False),
        (2.0, 5.0, 10.00, 5.00, "x", False),
        (1.5, 5.0, 10.00, 5.00, "x", False),
        (1.0, 5.0, 10.00, 5.00, "x", False),
        (0.5, 5.0, 10.00, 5.00, "x", False),
        # ---------------------------------
        # ----- ZAPATA ACHICANDOSE Y (Ly)--
        (5.0, 5.0, 10.00, 5.00, "y", True),
        (5.0, 4.5, 10.00, 5.00, "y", True),
        (5.0, 4.0, 10.00, 5.00, "y", True),
        (5.0, 3.5, 10.00, 5.00, "y", True),
        (5.0, 3.0, 10.00, 5.00, "y", True),
        (5.0, 2.5, 10.00, 5.00, "y", False),
        (5.0, 2.0, 10.00, 5.00, "y", False),
        (5.0, 1.5, 10.00, 5.00, "y", False),
        (5.0, 1.0, 10.00, 5.00, "y", False),
        (5.0, 0.5, 10.00, 5.00, "y", False),
        # ---------------------------------
        # ----- AXIAL CRECIENTE X ---------
        (6.0, 6.0, 7.000, 10.0, "x", False),
        (6.0, 6.0, 8.000, 10.0, "x", False),
        (6.0, 6.0, 9.000, 10.0, "x", False),
        (6.0, 6.0, 10.00, 10.0, "x", True),  # valor límite donde exentricidad=ly/6
        (6.0, 6.0, 11.00, 10.0, "x", True),
        (6.0, 6.0, 12.00, 10.0, "x", True),
        (6.0, 6.0, 13.00, 10.0, "x", True),
        # ---------------------------------
        # ----- AXIAL CRECIENTE Y ---------
        (6.0, 6.0, 7.000, 10.0, "y", False),
        (6.0, 6.0, 8.000, 10.0, "y", False),
        (6.0, 6.0, 9.000, 10.0, "y", False),
        (6.0, 6.0, 10.00, 10.0, "y", True),  # valor límite donde exentricidad=ly/6
        (6.0, 6.0, 11.00, 10.0, "y", True),
        (6.0, 6.0, 12.00, 10.0, "y", True),
        (6.0, 6.0, 13.00, 10.0, "y", True),
        # ---------------------------------
        # ----- CASOS ESPECIALES AXIAL ----
        (6.0, 6.0, -10.0, 5.00, "x", False),  # axial negativo
        (6.0, 6.0, 0.000, 5.00, "x", False),  # axial cero
        # ---------------------------------
        # ----- MOMENTO CRECIENTE X ---
        (3.0, 3.0, 10.00, -20.0, "x", False),
        (3.0, 3.0, 10.00, -10.0, "x", False),
        (3.0, 3.0, 10.00, -5.00, "x", True),  # valor límite donde exentricidad=ly/6
        (3.0, 3.0, 10.00, -2.00, "x", True),
        (3.0, 3.0, 10.00, 0.000, "x", True),
        (3.0, 3.0, 10.00, 2.000, "x", True),
        (3.0, 3.0, 10.00, 5.000, "x", True),  # valor límite donde exentricidad=ly/6
        (3.0, 3.0, 10.00, 10.00, "x", False),
        (3.0, 3.0, 10.00, 20.00, "x", False),
        # ---------------------------------
        # ----- MOMENTO CRECIENTE Y ---
        (3.0, 3.0, 10.00, -20.0, "y", False),
        (3.0, 3.0, 10.00, -10.0, "y", False),
        (3.0, 3.0, 10.00, -5.00, "y", True),  # valor límite donde exentricidad=ly/6
        (3.0, 3.0, 10.00, -2.00, "y", True),
        (3.0, 3.0, 10.00, 0.000, "y", True),
        (3.0, 3.0, 10.00, 2.000, "y", True),
        (3.0, 3.0, 10.00, 5.000, "y", True),  # valor límite donde exentricidad=ly/6
        (3.0, 3.0, 10.00, 10.00, "y", False),
        (3.0, 3.0, 10.00, 20.00, "y", False),
        # ---------------------------------
    ],
)
def test_ley_del_tercio_central(  # noqa: PLR0913
    lx: float, ly: float, axial: float, momento: float, direccion: Literal["x", "y"], expected_result: bool
) -> None:
    """Prueba la función ley_del_tercio_central de la clase Fundacion.

    Verifica que la función retorna el resultado correcto para diferentes casos de prueba.

    Args:
        lx: Longitud en la dimensión X de la fundación.
        ly: Longitud en la dimensión Y de la fundación.
        axial: Carga axial.
        momento: Momento.
        direccion: Dirección de la carga ("x" o "y").
        expected_result: Resultado esperado de la ley del tercio central para los valores dados.
    """
    fundacion = Fundacion(lx=lx, ly=ly, lz=randint(1, 100))
    assert fundacion.ley_del_tercio_central(axial, momento, direccion) == expected_result


def test_ley_del_tercio_central_invalid_direccion() -> None:
    """Dirección no válida."""
    fundacion = Fundacion(lx=6.0, ly=6.0, lz=1.0)

    with pytest.raises(ValueError, match="dirección debe ser 'x' o 'y'"):
        fundacion.ley_del_tercio_central(10.0, 5.0, "z")  # type: ignore


@pytest.mark.parametrize(
    "lx, ly, axial, momento, direccion, expected_result",
    [
        # ----- ZAPATA ACHICANDOSE X (Lx)--
        (5.0, 5.0, 10.00, 5.00, "x", False),
        (4.5, 5.0, 10.00, 5.00, "x", False),
        (4.0, 5.0, 10.00, 5.00, "x", False),
        (3.5, 5.0, 10.00, 5.00, "x", False),
        (3.0, 5.0, 10.00, 5.00, "x", False),  # valor límite donde excentricidad=lx/6
        (2.5, 5.0, 10.00, 5.00, "x", True),
        (2.3, 5.0, 10.00, 5.00, "x", True),
        (2.1, 5.0, 10.00, 5.00, "x", True),
        (2.0, 5.0, 10.00, 5.00, "x", True),  # valor límite donde excentricidad=lx/4
        (1.5, 5.0, 10.00, 5.00, "x", False),
        (1.0, 5.0, 10.00, 5.00, "x", False),
        (0.5, 5.0, 10.00, 5.00, "x", False),
        # ---------------------------------
        # ----- ZAPATA ACHICANDOSE Y (Ly)--
        (5.0, 5.0, 10.00, 5.00, "y", False),
        (5.0, 4.5, 10.00, 5.00, "y", False),
        (5.0, 4.0, 10.00, 5.00, "y", False),
        (5.0, 3.5, 10.00, 5.00, "y", False),
        (5.0, 3.0, 10.00, 5.00, "y", False),  # valor límite donde excentricidad=ly/6
        (5.0, 2.5, 10.00, 5.00, "y", True),
        (5.0, 2.3, 10.00, 5.00, "y", True),
        (5.0, 2.1, 10.00, 5.00, "y", True),
        (5.0, 2.0, 10.00, 5.00, "y", True),  # valor límite donde excentricidad=ly/4
        (5.0, 1.5, 10.00, 5.00, "y", False),
        (5.0, 1.0, 10.00, 5.00, "y", False),
        (5.0, 0.5, 10.00, 5.00, "y", False),
        # ---------------------------------
        # ----- AXIAL CRECIENTE X ---------
        (4.0, 3.0, 5.000, 10.0, "x", False),
        (4.0, 3.0, 8.000, 10.0, "x", False),
        (4.0, 3.0, 10.00, 10.0, "x", True),  # valor límite donde exentricidad=ly/4
        (4.0, 3.0, 11.00, 10.0, "x", True),
        (4.0, 3.0, 12.00, 10.0, "x", True),
        (4.0, 3.0, 13.00, 10.0, "x", True),
        (4.0, 3.0, 14.00, 10.0, "x", True),
        (4.0, 3.0, 15.00, 10.0, "x", False),  # valor límite donde exentricidad=ly/6
        (4.0, 3.0, 17.00, 10.0, "x", False),
        (4.0, 3.0, 20.00, 10.0, "x", False),
        (4.0, 3.0, 25.00, 10.0, "x", False),
        # ---------------------------------
        # ----- AXIAL CRECIENTE Y ---------
        (4.0, 3.0, 5.000, 10.0, "y", False),
        (4.0, 3.0, 10.00, 10.0, "y", False),
        (4.0, 3.0, 13.34, 10.0, "y", True),  # valor límite donde exentricidad=lx/4
        (4.0, 3.0, 14.00, 10.0, "y", True),
        (4.0, 3.0, 15.00, 10.0, "y", True),
        (4.0, 3.0, 16.00, 10.0, "y", True),
        (4.0, 3.0, 17.00, 10.0, "y", True),
        (4.0, 3.0, 18.00, 10.0, "y", True),
        (4.0, 3.0, 19.00, 10.0, "y", True),
        (4.0, 3.0, 20.00, 10.0, "y", False),  # valor límite donde exentricidad=lx/6
        (4.0, 3.0, 21.00, 10.0, "y", False),
        (4.0, 3.0, 25.00, 10.0, "y", False),
        (4.0, 3.0, 40.00, 10.0, "y", False),
        # ---------------------------------
        # ----- CASOS ESPECIALES AXIAL ----
        (6.0, 6.0, -10.0, 5.00, "x", False),  # axial negativo
        (6.0, 6.0, 0.000, 5.00, "x", False),  # axial cero
        # ---------------------------------
        # ----- MOMENTO CRECIENTE X ---
        (4.0, 8.0, 10.00, -15.0, "x", False),
        (4.0, 8.0, 10.00, -10.0, "x", True),
        (4.0, 8.0, 10.00, -7.00, "x", True),
        (4.0, 8.0, 10.00, -5.00, "x", False),
        (4.0, 8.0, 10.00, 5.000, "x", False),
        (4.0, 8.0, 10.00, 7.000, "x", True),
        (4.0, 8.0, 10.00, 10.00, "x", True),
        (4.0, 8.0, 10.00, 15.00, "x", False),
        # ---------------------------------
        # ----- MOMENTO CRECIENTE Y ---
        (4.0, 8.0, 10.00, -30.0, "y", False),
        (4.0, 8.0, 10.00, -20.0, "y", True),
        (4.0, 8.0, 10.00, -15.0, "y", True),
        (4.0, 8.0, 10.00, -10.0, "y", False),
        (4.0, 8.0, 10.00, -5.00, "y", False),
        (4.0, 8.0, 10.00, 0.000, "y", False),
        (4.0, 8.0, 10.00, 5.000, "y", False),
        (4.0, 8.0, 10.00, 10.00, "y", False),
        (4.0, 8.0, 10.00, 15.00, "y", True),
        (4.0, 8.0, 10.00, 20.00, "y", True),
        (4.0, 8.0, 10.00, 30.00, "y", False),
        # ---------------------------------
    ],
)
def test_ley_del_triangulo(  # noqa: PLR0913
    lx: float, ly: float, axial: float, momento: float, direccion: Literal["x", "y"], expected_result: bool
) -> None:
    """Prueba la función ley_del_triangulo de la clase Fundacion.

    Verifica que la función retorna el resultado correcto para diferentes casos de prueba.

    Args:
        lx: Longitud en la dimensión X de la fundación.
        ly: Longitud en la dimensión Y de la fundación.
        axial: Carga axial.
        momento: Momento.
        direccion: Dirección de la carga ("x" o "y").
        expected_result: Resultado esperado de la ley del tercio central para los valores dados.
    """
    fundacion = Fundacion(lx=lx, ly=ly, lz=randint(1, 100))
    assert fundacion.ley_del_triangulo(axial, momento, direccion) == expected_result


def test_ley_del_triangulo_invalid_direccion() -> None:
    """Dirección no válida."""
    fundacion = Fundacion(lx=6.0, ly=6.0, lz=1.0)

    with pytest.raises(ValueError, match="dirección debe ser 'x' o 'y'"):
        fundacion.ley_del_triangulo(10.0, 5.0, "z")  # type: ignore
