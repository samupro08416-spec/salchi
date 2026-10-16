import sys, json, time, zlib, base64, pickle, os
from chars import MODELS
names = sys.argv[1:] or list(MODELS)
store = {}
if os.path.exists('store.pkl'): store = pickle.load(open('store.pkl', 'rb'))
for nm in names:
    t = time.time(); m, (lo, hi) = MODELS[nm]()
    nv, nt = m.bake(lo, hi, h=float(getattr(m, 'voxel', 0.024)))
    store[nm] = m.export()
    print(nm, nv, 'verts', nt, 'tris', round(time.time() - t, 1), 's')
pickle.dump(store, open('store.pkl', 'wb'))
order = [k for k in MODELS if k in store]
heads = {}; blob = b''
for k in order:
    h, b = store[k]; h['off'] = len(blob); heads[k] = h; blob += b
c = zlib.compressobj(9, zlib.DEFLATED, -15); z = c.compress(blob) + c.flush()
b64 = base64.b64encode(z).decode()
json.dump({'heads': heads, 'z': b64}, open('models.json', 'w'), separators=(',', ':'))
print('raw', len(blob) // 1024, 'KB  deflate', len(z) // 1024, 'KB  base64', len(b64) // 1024, 'KB')
