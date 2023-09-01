# fastruct

## Structural analysis and design made fast and simple

Command line application (CLI) to analyse and design simple structures.

Written in python.

### Current capabilities

- Rigid foundation analysis: soil stress and lifting percentaje.

## Installation

```bash
pip install fastruct
```

or using virtualenv

```bash
python -m pip install fastruct
```

## Usage

### Adding new 1x1x1 foundation

```bash
$ fastruct f add 1 2 3
fundacion.id=1
```

### Adding loads (p vx, vy, mx, my) to foundation with ID=1

```bash
$ fastruct l add 1 1 1 1 1 1
user_load.id=1

$ fastruct l add 1 2.5 0.1 -0.5 -0.1 0.25
user_load.id=2
```

### Computing results for foundation with ID=1

```bash
$ fastruct f analize 1
             F001: Lx=1.00 Ly=2.00 Lz=3.00 Depth=3.00
┏━━━━┳━━━━━━┳━━━━━━┳━━━━━┳━━━━━━┳━━━━━━┳━━━━━┳━━━━━━━━━━━━┳━━━━━━┓
┃ #  ┃ NAME ┃ P    ┃ Vx  ┃ Vy   ┃ Mx   ┃ My  ┃ σ (ton/m²) ┃ %    ┃
┡━━━━╇━━━━━━╇━━━━━━╇━━━━━╇━━━━━━╇━━━━━━╇━━━━━╇━━━━━━━━━━━━╇━━━━━━┩
│ 01 │      │ 16.0 │ 1.0 │ 1.0  │ 4.0  │ 4.0 │ 39.00      │ 83%  │
├────┼──────┼──────┼─────┼──────┼──────┼─────┼────────────┼──────┤
│ 02 │      │ 17.5 │ 0.1 │ -0.5 │ -1.6 │ 0.6 │ 18.76      │ 100% │
└────┴──────┴──────┴─────┴──────┴──────┴─────┴────────────┴──────┘
```
