"""Personajes esculpidos con campos de distancia. Cada uno mira hacia +x, con el suelo en y=0,
con las mismas medidas que la versión anterior para que los trajes y accesorios encajen."""
import numpy as np
from sdf import Model, Ell, Cone, Xf

def ss(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)

COAT, DARK, LIGHT, EXTRA = 0, 1, 2, 3

# ---------------------------------------------------------------- Salchi (perro salchicha)
def dog():
    legs = [('legFL', (0.5, 0.58, 0.2)), ('legFR', (0.5, 0.58, -0.2)), ('legBL', (-0.6, 0.58, 0.2)), ('legBR', (-0.6, 0.58, -0.2))]
    bones = [('body', None, (0, 0, 0)), ('head', 'body', (1.02, 1.36, 0)), ('earL', 'head', (0.95, 1.56, 0.3)), ('earR', 'head', (0.95, 1.56, -0.3)),
             ('tail', 'body', (-1.02, 0.9, 0))] + [(n, 'body', p) for n, p in legs]
    m = Model('dog', bones); m.voxel = 0.031
    B = 'body'
    # Tronco largo y bajo, pecho profundo (quilla) y grupa redondeada
    m.add(Cone((-0.72, 0.8, 0), (0.6, 0.8, 0), 0.36, 0.38, bone=B, k=0.0),
          Ell((0.6, 0.72, 0), (0.36, 0.42, 0.32), bone=B, k=0.2),                         # pecho profundo
          Ell((-0.78, 0.82, 0), (0.32, 0.34, 0.32), bone=B, k=0.15),                      # grupa
          Ell((0.0, 0.58, 0), (0.7, 0.16, 0.24), bone=B, k=0.22))                         # barriga
    m.add(Cone((0.68, 0.96, 0), (0.96, 1.27, 0), 0.3, 0.25, bone=B, k=0.12))           # cuello
    H = 'head'
    m.add(Ell((1.02, 1.38, 0), (0.4, 0.35, 0.33), bone=H, k=0.1),
          Ell((0.92, 1.53, 0), (0.27, 0.12, 0.26), bone=H, k=0.12),
          Cone((1.17, 1.32, 0), (1.62, 1.23, 0), 0.21, 0.12, bone=H, k=0.14),
          Ell((1.36, 1.17, 0), (0.24, 0.08, 0.13), bone=H, region=LIGHT, k=0.08),
          Ell((1.67, 1.24, 0), (0.06, 0.075, 0.09), bone=H, k=0.05))
    m.mirrorZ(lambda s: [Ell((1.24, 1.31, 0.12 * s), (0.18, 0.1, 0.09), bone=H, k=0.08),
                         Ell((1.13, 1.48, 0.16 * s), (0.07, 0.045, 0.055), bone=H, region=LIGHT, k=0.04)])
    for s, bn in ((1, 'earL'), (-1, 'earR')):
        m.add(Ell((0.88, 1.28, 0.35 * s), (0.17, 0.31, 0.055), rot=(0.16 * s, 0, 0.14), bone=bn, region=DARK, k=0.04),
              Ell((0.93, 1.52, 0.31 * s), (0.11, 0.08, 0.05), rot=(0.3 * s, 0, 0), bone=bn, region=DARK, k=0.05))
    for n, (x, y, z) in legs:
        front = x > 0
        m.add(Ell((x - (0 if front else 0.04), 0.6, z * 1.05), (0.15 if front else 0.2, 0.2, 0.13), bone=n, k=0.1),
              Cone((x, 0.5, z), (x + 0.04, 0.12, z), 0.115, 0.095, bone=n, k=0.06),
              Ell((x + 0.09, 0.065, z), (0.16, 0.075, 0.12), bone=n, region=DARK, k=0.05))
    m.add(Cone((-0.98, 0.9, 0), (-1.48, 1.22, 0), 0.085, 0.026, bone='tail', k=0.06))
    # Patrones: pecho y barriga claros, lomo algo más oscuro, boca clara
    m.patterns.append((lambda p: ss(0.66, 0.52, p[:, 1]) * ss(0.36, 0.46, p[:, 1]) * ss(0.3, 0.14, np.abs(p[:, 2])) * ss(0.95, 0.8, p[:, 0]) * ss(-0.95, -0.8, p[:, 0]), LIGHT))
    m.patterns.append((lambda p: 0.8 * ss(0.62, 0.78, p[:, 0]) * ss(0.98, 0.8, p[:, 0]) * ss(1.0, 0.75, p[:, 1]) * ss(0.42, 0.55, p[:, 1]) * ss(0.3, 0.12, np.abs(p[:, 2])), LIGHT))
    m.patterns.append((lambda p: 0.5 * ss(1.02, 1.17, p[:, 1]) * ss(0.7, 0.5, p[:, 0]) * ss(-1.1, -0.9, p[:, 0]), DARK))
    m.patterns.append((lambda p: ss(1.27, 1.2, p[:, 1]) * ss(1.12, 1.28, p[:, 0]), LIGHT))
    for s in (1, -1):
        m.anchor('eye' + ('L' if s > 0 else 'R'), (1.04, 1.42, 0), (0.62, 0.24, 0.75 * s), inset=0.03)
    m.anchor('nose', (1.55, 1.25, 0), (1, 0.12, 0))
    m.anchor('top', (1.0, 1.38, 0), (0, 1, 0))
    m.extra = {'collar': [[0.8, 1.08, 0], 0.29]}
    return m, ((-1.6, -0.05, -0.6), (1.85, 1.85, 0.6))


def tail_chain(m, pts, r0, r1, bone, region=COAT, k=0.05):
    n = len(pts) - 1
    for i in range(n):
        ra = r0 + (r1 - r0) * i / n; rb = r0 + (r1 - r0) * (i + 1) / n
        m.add(Cone(pts[i], pts[i + 1], ra, rb, bone=bone, region=region, k=k))

# ---------------------------------------------------------------- Miso (gata blanca de pelo largo)
def cat():
    legs = [('legFL', (0.45, 0.62, 0.17)), ('legFR', (0.45, 0.62, -0.17)), ('legBL', (-0.45, 0.62, 0.17)), ('legBR', (-0.45, 0.62, -0.17))]
    bones = [('body', None, (0, 0, 0)), ('head', 'body', (0.82, 1.42, 0)), ('tail', 'body', (-0.66, 0.95, 0))] + [(n, 'body', p) for n, p in legs]
    m = Model('cat', bones); m.voxel = 0.03
    B = 'body'
    m.add(Ell((0.0, 0.86, 0), (0.72, 0.36, 0.34), bone=B, k=0.0),
          Ell((0.45, 0.86, 0), (0.32, 0.38, 0.32), bone=B, k=0.18),             # pecho
          Ell((-0.45, 0.88, 0), (0.32, 0.36, 0.33), bone=B, k=0.16),            # caderas
          Ell((0.6, 0.86, 0), (0.18, 0.26, 0.24), bone=B, region=LIGHT, k=0.12))  # gorguera del pecho
    m.add(Cone((0.5, 1.0, 0), (0.76, 1.3, 0), 0.25, 0.22, bone=B, k=0.12))
    H = 'head'
    m.add(Ell((0.84, 1.42, 0), (0.36, 0.33, 0.37), bone=H, k=0.08),
          Ell((1.08, 1.33, 0), (0.15, 0.12, 0.17), bone=H, k=0.1),               # hocico corto
          Ell((1.06, 1.25, 0), (0.1, 0.06, 0.1), bone=H, region=LIGHT, k=0.05))  # barbilla
    m.mirrorZ(lambda s: [Ell((0.98, 1.3, 0.2 * s), (0.17, 0.15, 0.13), bone=H, k=0.1),               # mofletes peludos
                         Xf(Cone((0, 0, 0), (0, 0.26, 0), 0.13, 0.012), (0.76, 1.66, 0.22 * s), scale=(0.45, 1, 1), rot=(-0.38 * s, 0.4 * s, 0.05), bone=H, k=0.05),
                         Xf(Cone((0, 0, 0), (0, 0.2, 0), 0.09, 0.01), (0.8, 1.67, 0.21 * s), scale=(0.3, 1, 1), rot=(-0.38 * s, 0.4 * s, 0.05), bone=H, region=EXTRA, k=0.02)])
    for n, (x, y, z) in legs:
        front = x > 0
        m.add(Ell((x - (0 if front else 0.05), 0.68, z), (0.13 if front else 0.19, 0.22, 0.12), bone=n, k=0.1),
              Cone((x, 0.56, z), (x + (0.02 if front else -0.03), 0.1, z), 0.085, 0.07, bone=n, k=0.06),
              Ell((x + 0.05, 0.055, z), (0.11, 0.06, 0.09), bone=n, k=0.05))
    tail_chain(m, [(-0.62, 0.95, 0), (-0.95, 1.05, 0), (-1.12, 1.32, 0), (-1.1, 1.62, 0), (-0.98, 1.8, 0)], 0.085, 0.06, 'tail', k=0.05)
    m.add(Ell((-0.98, 1.82, 0), (0.08, 0.08, 0.08), bone='tail', k=0.05))
    for s_ in (1, -1):
        m.anchor('eye' + ('L' if s_ > 0 else 'R'), (0.9, 1.46, 0), (0.75, 0.12, 0.62 * s_), inset=0.03)
    m.anchor('nose', (1.1, 1.36, 0), (1, 0.2, 0))
    m.anchor('top', (0.82, 1.42, 0), (0, 1, 0))
    m.extra = {'collar': [[0.64, 1.12, 0], 0.25]}
    return m, ((-1.3, -0.05, -0.55), (1.35, 2.0, 0.55))

# ---------------------------------------------------------------- Rocco (american staffordshire cachorro)
def rocco():
    legs = [('legFL', (0.4, 0.6, 0.24)), ('legFR', (0.4, 0.6, -0.24)), ('legBL', (-0.42, 0.6, 0.23)), ('legBR', (-0.42, 0.6, -0.23))]
    bones = [('body', None, (0, 0, 0)), ('head', 'body', (0.84, 1.42, 0)), ('earL', 'head', (0.78, 1.7, 0.27)), ('earR', 'head', (0.78, 1.7, -0.27)),
             ('tail', 'body', (-0.62, 0.98, 0))] + [(n, 'body', p) for n, p in legs]
    m = Model('rocco', bones); m.voxel = 0.03
    B = 'body'
    m.add(Ell((0.02, 0.9, 0), (0.62, 0.4, 0.4), bone=B, k=0.0),
          Ell((0.38, 0.92, 0), (0.38, 0.46, 0.45), bone=B, k=0.18),               # pecho ancho y musculoso
          Ell((0.5, 0.78, 0), (0.24, 0.3, 0.3), bone=B, region=LIGHT, k=0.14),    # pechera blanca
          Ell((-0.42, 0.92, 0), (0.3, 0.36, 0.38), bone=B, k=0.15))
    m.add(Cone((0.52, 1.06, 0), (0.78, 1.32, 0), 0.34, 0.3, bone=B, k=0.12))          # cuello grueso
    H = 'head'
    m.add(Ell((0.84, 1.45, 0), (0.38, 0.35, 0.42), bone=H, k=0.08),                     # cabeza ancha
          Ell((1.12, 1.34, 0), (0.2, 0.17, 0.26), bone=H, region=LIGHT, k=0.1),         # hocico corto y ancho
          Ell((1.1, 1.22, 0), (0.15, 0.08, 0.17), bone=H, region=LIGHT, k=0.06),
          Ell((0.98, 1.58, 0), (0.18, 0.05, 0.06), bone=H, region=LIGHT, k=0.06))       # lista blanca en la frente
    m.mirrorZ(lambda s: [Ell((0.98, 1.36, 0.25 * s), (0.2, 0.17, 0.12), bone=H, k=0.1)])  # carrillos fuertes
    for s, bn in ((1, 'earL'), (-1, 'earR')):
        m.add(Xf(Cone((0, 0, 0), (0, 0.24, 0), 0.15, 0.035), (0.76, 1.7, 0.28 * s), scale=(0.3, 1, 1), rot=(-1.0 * s, 0.5 * s, -0.75), bone=bn, region=DARK, k=0.035))
    for n, (x, y, z) in legs:
        front = x > 0
        m.add(Ell((x - (0 if front else 0.04), 0.66, z), (0.17 if front else 0.21, 0.24, 0.15), bone=n, k=0.1),
              Cone((x, 0.52, z), (x + 0.02, 0.11, z), 0.13, 0.11, bone=n, k=0.06),
              Ell((x + 0.06, 0.06, z), (0.15, 0.07, 0.13), bone=n, region=LIGHT, k=0.05))
    m.add(Cone((-0.58, 0.98, 0), (-0.98, 1.2, 0), 0.08, 0.025, bone='tail', k=0.06))
    m.patterns.append((lambda p: ss(0.62, 0.5, p[:, 1]) * ss(0.4, 0.2, np.abs(p[:, 2])) * ss(0.9, 0.5, p[:, 0]) * ss(-0.5, -0.2, p[:, 0]), LIGHT))
    m.patterns.append((lambda p: ss(0.22, 0.14, p[:, 1]), LIGHT))   # calcetines blancos
    for s_ in (1, -1):
        m.anchor('eye' + ('L' if s_ > 0 else 'R'), (0.9, 1.48, 0), (0.7, 0.18, 0.62 * s_), inset=0.03)
    m.anchor('nose', (1.2, 1.38, 0), (1, 0.15, 0))
    m.anchor('top', (0.84, 1.45, 0), (0, 1, 0))
    m.extra = {'collar': [[0.66, 1.18, 0], 0.32]}
    return m, ((-1.15, -0.05, -0.62), (1.4, 1.95, 0.62))

# ---------------------------------------------------------------- Samu (monito)
def monkey():
    legs = [('legFL', (0.3, 0.74, 0.22)), ('legFR', (0.3, 0.74, -0.22)), ('legBL', (-0.3, 0.64, 0.22)), ('legBR', (-0.3, 0.64, -0.22))]
    bones = [('body', None, (0, 0, 0)), ('head', 'body', (0.6, 1.55, 0)), ('earL', 'head', (0.56, 1.6, 0.4)), ('earR', 'head', (0.56, 1.6, -0.4)),
             ('tail', 'body', (-0.48, 0.95, 0))] + [(n, 'body', p) for n, p in legs]
    m = Model('monkey', bones); m.voxel = 0.03
    B = 'body'
    m.add(Ell((0.02, 0.95, 0), (0.48, 0.42, 0.38), rot=(0, 0, 0.25), bone=B, k=0.0),
          Ell((0.2, 0.9, 0), (0.3, 0.34, 0.3), bone=B, region=LIGHT, k=0.12),          # barriguita clara
          Cone((0.3, 1.15, 0), (0.52, 1.38, 0), 0.25, 0.22, bone=B, k=0.12))
    H = 'head'
    m.add(Ell((0.6, 1.56, 0), (0.37, 0.36, 0.38), bone=H, k=0.08),
          Ell((0.84, 1.58, 0), (0.14, 0.2, 0.28), bone=H, region=LIGHT, k=0.1),           # máscara de la cara
          Ell((0.9, 1.42, 0), (0.17, 0.14, 0.2), bone=H, region=LIGHT, k=0.1),            # morrito
          Ell((0.72, 1.82, 0), (0.18, 0.07, 0.16), bone=H, k=0.08))                       # tupé
    m.mirrorZ(lambda s: [Ell((0.82, 1.62, 0.12 * s), (0.12, 0.13, 0.12), bone=H, region=LIGHT, k=0.08)])
    for s, bn in ((1, 'earL'), (-1, 'earR')):
        m.add(Xf(Ell((0, 0, 0), (0.15, 0.15, 0.05)), (0.56, 1.6, 0.41 * s), rot=(0, 0.3 * s, 0), bone=bn, k=0.05),
              Xf(Ell((0, 0, 0), (0.09, 0.09, 0.03)), (0.58, 1.6, 0.44 * s), rot=(0, 0.3 * s, 0), bone=bn, region=LIGHT, k=0.02))
    for n, (x, y, z) in legs:
        front = x > 0
        m.add(Ell((x, y + 0.02, z * 0.95), (0.14, 0.18, 0.13), bone=n, k=0.1),
              Cone((x, y - 0.08, z), (x + 0.03, 0.1, z), 0.095, 0.075, bone=n, k=0.06),
              Ell((x + 0.07, 0.05, z), (0.13, 0.06, 0.1), bone=n, region=LIGHT if front else DARK, k=0.05))
    tail_chain(m, [(-0.44, 0.95, 0), (-0.8, 0.98, 0), (-1.05, 1.2, 0), (-1.08, 1.5, 0), (-0.92, 1.66, 0), (-0.78, 1.56, 0), (-0.82, 1.42, 0)], 0.06, 0.035, 'tail', k=0.04)
    for s_ in (1, -1):
        m.anchor('eye' + ('L' if s_ > 0 else 'R'), (0.8, 1.6, 0.12 * s_), (1, 0.05, 0.25 * s_), inset=0.035)
    m.anchor('nose', (0.95, 1.45, 0), (1, 0.15, 0))
    m.anchor('top', (0.6, 1.56, 0), (0, 1, 0))
    m.extra = {'collar': [[0.44, 1.22, 0], 0.27]}
    return m, ((-1.25, -0.05, -0.62), (1.15, 2.05, 0.62))

# ---------------------------------------------------------------- DylonBaby30 (tortuga ninja original)
def turtle():
    legs = [('legFL', (0.38, 0.42, 0.32)), ('legFR', (0.38, 0.42, -0.32)), ('legBL', (-0.38, 0.42, 0.32)), ('legBR', (-0.38, 0.42, -0.32))]
    bones = [('body', None, (0, 0, 0)), ('head', 'body', (0.84, 0.8, 0)), ('tail', 'body', (-0.62, 0.45, 0))] + [(n, 'body', p) for n, p in legs]
    m = Model('turtle', bones); m.voxel = 0.026
    B = 'body'
    m.add(Ell((-0.02, 0.56, 0), (0.64, 0.36, 0.56), bone=B, region=DARK, k=0.0),          # caparazón
          Ell((-0.02, 0.44, 0), (0.68, 0.06, 0.6), bone=B, region=DARK, k=0.06),          # borde
          Ell((0.0, 0.38, 0), (0.56, 0.12, 0.46), bone=B, region=LIGHT, k=0.05))          # peto
    m.add(Cone((0.5, 0.56, 0), (0.78, 0.74, 0), 0.13, 0.12, bone='head', k=0.06))
    H = 'head'
    m.add(Ell((0.86, 0.8, 0), (0.29, 0.25, 0.25), bone=H, k=0.06),
          Ell((1.06, 0.74, 0), (0.12, 0.11, 0.17), bone=H, k=0.08),
          Ell((-0.0 + 0.6, 0.86, 0), (0.06, 0.06, 0.06), bone=H, region=EXTRA, k=0.03))      # nudo del pañuelo
    m.add(Ell((0.56, 0.86, 0.0), (0.05, 0.12, 0.03), rot=(0, 0, 0.6), bone=H, region=EXTRA, k=0.03))
    for n, (x, y, z) in legs:
        m.add(Cone((x * 0.92, 0.42, z * 0.9), (x * 1.05, 0.1, z * 1.08), 0.12, 0.105, bone=n, k=0.07),
              Ell((x * 1.08 + 0.04, 0.06, z * 1.1), (0.15, 0.07, 0.12), bone=n, k=0.05))
    m.add(Cone((-0.6, 0.45, 0), (-0.82, 0.38, 0), 0.07, 0.02, bone='tail', k=0.05))
    # Capucha ninja: cubre la parte de arriba y de atrás de la cabeza, con antifaz alrededor de los ojos
    eyes = []
    for s_ in (1, -1):
        e, n_ = m.anchor('eye' + ('L' if s_ > 0 else 'R'), (0.9, 0.84, 0.08 * s_), (0.85, 0.2, 0.5 * s_), inset=0.035)
        eyes.append(e)
    ey = eyes[0][1]
    def hood(p):
        on_head = ss(0.52, 0.62, p[:, 0]) * ss(0.5, 0.6, p[:, 1])
        cap = np.maximum(ss(ey + 0.06, ey + 0.1, p[:, 1]), ss(0.8, 0.7, p[:, 0]))
        band = ss(ey - 0.085, ey - 0.06, p[:, 1]) * ss(ey + 0.1, ey + 0.07, p[:, 1])
        return on_head * np.maximum(cap, band)
    m.patterns.append((hood, EXTRA))
    for e in eyes:
        m.patterns.append((lambda p, e=e: ss(0.115, 0.095, np.linalg.norm(p - e, axis=1)), COAT))
    # Placas del caparazón: surcos más oscuros en una rejilla hexagonal
    def scutes(p):
        x, z, y = p[:, 0] + 0.02, p[:, 2], p[:, 1]
        top = ss(0.46, 0.52, y)
        sc = 0.28; q1 = x / sc; q2 = (x * 0.5 + z * 0.866) / sc; q3 = (-x * 0.5 + z * 0.866) / sc
        f = lambda q: np.abs(q - np.round(q))
        line = np.minimum(np.minimum(f(q1), f(q2)), f(q3))
        return 1 - top * 0.45 * ss(0.12, 0.03, line)
    m.shades.append(scutes)
    m.anchor('top', (0.86, 0.8, 0), (0, 1, 0))
    m.extra = {}
    return m, ((-0.95, -0.05, -0.78), (1.3, 1.15, 0.78))

MODELS = {'dog': dog, 'cat': cat, 'rocco': rocco, 'monkey': monkey, 'turtle': turtle}
