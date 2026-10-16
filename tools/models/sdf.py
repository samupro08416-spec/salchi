"""Modelado orgánico por campos de distancia (SDF): primitivas suaves que se funden,
marching cubes, pesos de piel para huesos y regiones de color. Exporta datos compactos."""
import numpy as np, json, base64, struct
from skimage import measure

def rot_matrix(e):
    if e is None: return np.eye(3)
    x, y, z = e
    cx, sx, cy, sy, cz, sz = np.cos(x), np.sin(x), np.cos(y), np.sin(y), np.cos(z), np.sin(z)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx   # mismo orden que three.js (XYZ)

class Prim:
    def __init__(self, bone=None, region=0, k=0.06, sub=False, mirror=False, name=None):
        self.bone, self.region, self.k, self.sub, self.name = bone, region, k, sub, name

class Ell(Prim):
    def __init__(self, c, r, rot=None, **kw):
        super().__init__(**kw); self.c = np.array(c, float); self.r = np.array(r, float); self.R = rot_matrix(rot)
    def d(self, p):
        q = (p - self.c) @ self.R          # a coordenadas locales (R^T aplicado por la derecha)
        k0 = np.linalg.norm(q / self.r, axis=-1)
        k1 = np.linalg.norm(q / (self.r * self.r), axis=-1) + 1e-9
        return k0 * (k0 - 1.0) / k1

class Cone(Prim):
    """Cápsula con radio variable (round cone) de a a b."""
    def __init__(self, a, b, r1, r2, **kw):
        super().__init__(**kw); self.a = np.array(a, float); self.b = np.array(b, float); self.r1, self.r2 = r1, r2
    def d(self, p):
        a, b, r1, r2 = self.a, self.b, self.r1, self.r2
        ba = b - a; l2 = ba @ ba; rr = r1 - r2; a2 = l2 - rr * rr; il2 = 1.0 / l2
        pa = p - a; y = pa @ ba; z = y - l2
        w = pa * l2 - y[..., None] * ba
        x2 = np.sum(w * w, axis=-1); y2 = y * y * l2; z2 = z * z * l2
        k = np.sign(rr) * rr * rr * x2
        d3 = (np.sqrt(np.maximum(x2 * a2 * il2, 0)) + y * rr) * il2 - r1
        d1 = np.sqrt(x2 + z2) * il2 - r2
        d2 = np.sqrt(x2 + y2) * il2 - r1
        return np.where(np.sign(z) * a2 * z2 > k, d1, np.where(np.sign(y) * a2 * y2 < k, d2, d3))

class Xf(Prim):
    """Primitiva transformada: escala no uniforme + rotación alrededor de c (la primitiva está en coordenadas locales)."""
    def __init__(self, inner, c, scale=(1, 1, 1), rot=None, **kw):
        super().__init__(**kw); self.inner = inner; self.c = np.array(c, float); self.s = np.array(scale, float); self.R = rot_matrix(rot)
    def d(self, p):
        q = ((p - self.c) @ self.R) / self.s
        return self.inner.d(q) * self.s.min()

def smin(a, b, k):
    if k <= 0: return np.minimum(a, b)
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)

def smax(a, b, k):
    return -smin(-a, -b, k)

class Model:
    def __init__(self, name, bones):
        self.name = name; self.bones = bones   # lista de (nombre, padre, posición)
        self.prims = []; self.patterns = []; self.anchors = {}; self.shades = []; self.furfns = []
    def add(self, *ps):
        for p in ps: self.prims.append(p)
    def mirrorZ(self, make):
        """make(s) crea primitivas para el lado s (+1/-1)."""
        for s in (1, -1): self.add(*make(s))
    def field(self, p, each=False):
        d = None; ds = []
        for pr in self.prims:
            di = pr.d(p)
            if each: ds.append(di)
            if d is None: d = di
            elif pr.sub: d = smax(d, -di, pr.k)
            else: d = smin(d, di, pr.k)
        return (d, ds) if each else d
    def normal(self, p, e=0.004):
        ex = np.array([e, 0, 0]); ey = np.array([0, e, 0]); ez = np.array([0, 0, e])
        n = np.stack([self.field(p + ex) - self.field(p - ex), self.field(p + ey) - self.field(p - ey), self.field(p + ez) - self.field(p - ez)], -1)
        return n / (np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9)
    def surface(self, origin, direction, tmax=2.0):
        o = np.array(origin, float); dv = np.array(direction, float); dv /= np.linalg.norm(dv)
        # empieza dentro y avanza hasta salir
        t = 0.0
        for _ in range(400):
            d = self.field((o + dv * t)[None])[0]
            if d > 0: break
            t += max(0.002, -d * 0.5)
        # refina con bisección
        lo, hi = max(0, t - 0.02), t
        for _ in range(30):
            m = (lo + hi) / 2
            if self.field((o + dv * m)[None])[0] > 0: hi = m
            else: lo = m
        pt = o + dv * hi
        return pt, self.normal(pt[None])[0]
    def anchor(self, name, origin, direction, inset=0.0):
        pt, n = self.surface(origin, direction)
        self.anchors[name] = {'p': (pt - n * inset).round(4).tolist(), 'n': n.round(4).tolist()}
        return pt, n

    def bake(self, lo, hi, h=0.025, sigma_b=0.045, sigma_r=0.02):
        lo = np.array(lo, float); hi = np.array(hi, float)
        n = np.ceil((hi - lo) / h).astype(int) + 1
        xs = [lo[i] + np.arange(n[i]) * h for i in range(3)]
        X, Y, Z = np.meshgrid(*xs, indexing='ij')
        P = np.stack([X, Y, Z], -1).reshape(-1, 3)
        D = np.empty(len(P))
        for s in range(0, len(P), 400000): D[s:s + 400000] = self.field(P[s:s + 400000])
        D = D.reshape(n)
        verts, faces, _, _ = measure.marching_cubes(D, 0.0, spacing=(h, h, h))
        verts += lo
        faces = faces[:, [0, 2, 1]]       # orden antihorario mirando desde fuera
        nrm = self.normal(verts)
        # Si la normal media apunta hacia dentro, invierte los triángulos
        tri = verts[faces]; fn = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        if np.sum(fn * nrm[faces[:, 0]]) < 0: faces = faces[:, [0, 2, 1]]
        dmin, ds = self.field(verts, each=True)
        ds = np.stack(ds, 1)                       # (nv, nprims)
        add = np.array([not p.sub for p in self.prims])
        dd = np.where(add[None], ds, 1e3)
        m = dd.min(1, keepdims=True)
        # pesos de huesos
        bn = [b[0] for b in self.bones]
        infl = np.exp(-np.maximum(dd - m, 0) / sigma_b)
        W = np.zeros((len(verts), len(bn)))
        for i, p in enumerate(self.prims):
            if add[i]: W[:, bn.index(p.bone)] += infl[:, i]
        idx = np.argsort(-W, 1)[:, :2]
        w2 = np.take_along_axis(W, idx, 1); w2 = w2 / (w2.sum(1, keepdims=True) + 1e-9)
        # regiones de color
        inflr = np.exp(-np.maximum(dd - m, 0) / sigma_r)
        RW = np.zeros((len(verts), 4))
        for i, p in enumerate(self.prims):
            if add[i]: RW[:, p.region] += inflr[:, i]
        RW /= RW.sum(1, keepdims=True)
        for fn_, reg in self.patterns:
            w = np.clip(fn_(verts), 0, 1)[:, None]
            one = np.zeros(4); one[reg] = 1
            RW = RW * (1 - w) + one * w
        # oclusión ambiental: oscurece pliegues y huecos (bajo las orejas, entre patas...)
        occ = np.zeros(len(verts))
        for t, wt in ((0.025, 1.0), (0.06, 0.6), (0.11, 0.35), (0.18, 0.2)):
            occ += np.maximum(t - self.field(verts + nrm * t), 0) / t * wt
        ao = np.clip(1 - occ * 0.42, 0.45, 1)
        for fn_ in self.shades: ao = ao * np.clip(fn_(verts), 0, 1)
        self.ao = ao
        fm = np.ones(len(verts))
        for nm_, a in self.anchors.items():
            pa = np.array(a['p'])
            if nm_.startswith('eye'): fm *= np.clip((np.linalg.norm(verts - pa, axis=1) - 0.09) / 0.08, 0, 1)
            if nm_ == 'nose': fm *= 0.25 + 0.75 * np.clip((np.linalg.norm(verts - pa, axis=1) - 0.06) / 0.18, 0, 1)
        fm *= 0.55 + 0.45 * np.clip((verts[:, 1] - 0.06) / 0.12, 0, 1)
        fm *= 1 - 0.7 * RW[:, 3]
        for fn_ in self.furfns: fm = fm * np.clip(fn_(verts), 0, 1)
        self.fm = fm
        self.verts, self.faces, self.nrm, self.skin_i, self.skin_w, self.rw = verts, faces, nrm, idx, w2, RW
        return len(verts), len(faces)

    def export(self):
        """Binario plano y en deltas (comprime mucho mejor) + cabecera JSON."""
        v = self.verts; lo = v.min(0); hi = v.max(0); sc = hi - lo
        q = np.round((v - lo) / sc * 65535).astype(np.int64)
        planes = []
        for k in range(3):
            c = q[:, k]; d = np.diff(c, prepend=0) % 65536; planes.append(d.astype('<u2').tobytes())
        nq = np.round(np.clip(self.nrm, -1, 1) * 127).astype('i1')
        for k in range(3): planes.append(nq[:, k].tobytes())
        rw = np.round(self.rw * 255).astype('u1')
        for k in range(4): planes.append(rw[:, k].tobytes())
        si = self.skin_i.astype('u1')
        planes += [si[:, 0].tobytes(), si[:, 1].tobytes(), np.round(self.skin_w[:, 0] * 255).astype('u1').tobytes(), np.round(self.ao * 255).astype('u1').tobytes(), np.round(self.fm * 255).astype('u1').tobytes()]
        big = len(v) > 65535
        ix = self.faces.reshape(-1).astype(np.int64)
        dix = np.diff(ix, prepend=0) % (2 ** 32 if big else 65536)
        planes.append(dix.astype('<u4' if big else '<u2').tobytes())
        buf = b''.join(planes)
        head = {'nv': int(len(v)), 'nt': int(len(self.faces)), 'lo': lo.round(5).tolist(), 'sc': sc.round(5).tolist(), 'big': big, 'len': len(buf),
                'extra': getattr(self, 'extra', {}), 'bones': [{'n': b[0], 'p': b[1], 'pos': list(map(float, b[2]))} for b in self.bones], 'anchors': self.anchors}
        return head, buf
