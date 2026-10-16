  // ======================= MODELOS ESCULPIDOS (malla con esqueleto) =======================
  // Decodifica una malla empaquetada: posición (u16), normal (i8), regiones de color (u8x4), 2 huesos por vértice
  let MODEL_BLOB = null;
  function modelBlob(pack) {
    if (!MODEL_BLOB) { const bin = atob(pack.z), z = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) z[i] = bin.charCodeAt(i); MODEL_BLOB = inflateRaw(z); }
    return MODEL_BLOB;
  }
  function decodeModel(pack, key) {
    const h = pack.heads[key], blob = modelBlob(pack), nv = h.nv, nt = h.nt;
    let o = h.off;
    const u16 = n => { const a = new Uint16Array(n); for (let i = 0; i < n; i++) a[i] = blob[o + i * 2] | (blob[o + i * 2 + 1] << 8); o += n * 2; return a; };
    const u8 = n => { const a = blob.subarray(o, o + n); o += n; return a; };
    const pos = new Float32Array(nv * 3), nor = new Float32Array(nv * 3), rwA = new Float32Array(nv * 4), aoA = new Float32Array(nv);
    const skI = new Uint16Array(nv * 4), skW = new Float32Array(nv * 4);
    for (let k = 0; k < 3; k++) { const d = u16(nv); let acc = 0; for (let i = 0; i < nv; i++) { acc = (acc + d[i]) & 65535; pos[i * 3 + k] = h.lo[k] + acc / 65535 * h.sc[k]; } }
    for (let k = 0; k < 3; k++) { const d = u8(nv); for (let i = 0; i < nv; i++) nor[i * 3 + k] = ((d[i] << 24) >> 24) / 127; }
    for (let k = 0; k < 4; k++) { const d = u8(nv); for (let i = 0; i < nv; i++) rwA[i * 4 + k] = d[i] / 255; }
    const fmA = new Float32Array(nv);
    { const a = u8(nv), b = u8(nv), w = u8(nv), ao = u8(nv), fm = u8(nv); for (let i = 0; i < nv; i++) { skI[i * 4] = a[i]; skI[i * 4 + 1] = b[i]; skW[i * 4] = w[i] / 255; skW[i * 4 + 1] = 1 - w[i] / 255; aoA[i] = ao[i] / 255; fmA[i] = fm[i] / 255; } }
    let ix;
    if (h.big) { ix = new Uint32Array(nt * 3); let acc = 0; for (let i = 0; i < nt * 3; i++) { const d = (blob[o] | (blob[o + 1] << 8) | (blob[o + 2] << 16) | (blob[o + 3] << 24)) >>> 0; o += 4; acc = (acc + d) >>> 0; ix[i] = acc; } }
    else { const d = u16(nt * 3); ix = new Uint16Array(nt * 3); let acc = 0; for (let i = 0; i < nt * 3; i++) { acc = (acc + d[i]) & 65535; ix[i] = acc; } }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    g.setAttribute('normal', new THREE.BufferAttribute(nor, 3));
    g.setAttribute('rw', new THREE.BufferAttribute(rwA, 4));
    g.setAttribute('ao', new THREE.BufferAttribute(aoA, 1));
    g.setAttribute('fm', new THREE.BufferAttribute(fmA, 1));
    g.setAttribute('skinIndex', new THREE.BufferAttribute(skI, 4));
    g.setAttribute('skinWeight', new THREE.BufferAttribute(skW, 4));
    g.setIndex(new THREE.BufferAttribute(ix, 1));
    g.computeBoundingSphere();
    return { geo: g, head: h };
  }
  // Ruido de pelo: mechones finos que se repiten sin costuras
  const strandTex = (() => {
    const N = 256, c = document.createElement('canvas'); c.width = c.height = N; const x = c.getContext('2d'); if (!x) return null;
    const img = x.createImageData(N, N), d = img.data;
    for (let i = 0; i < N * N; i++) { const v = Math.random(); d[i * 4] = v * 255; d[i * 4 + 1] = Math.random() * 255; d[i * 4 + 2] = 255; d[i * 4 + 3] = 255; }
    x.putImageData(img, 0, 0);
    // manchas suaves en el canal azul para variación de tono
    for (let k = 0; k < 40; k++) { const px = Math.random() * N, py = Math.random() * N, r = 10 + Math.random() * 30; for (const ox of [-N, 0, N]) for (const oy of [-N, 0, N]) { const gr = x.createRadialGradient(px + ox, py + oy, 0, px + ox, py + oy, r); gr.addColorStop(0, 'rgba(0,0,0,.18)'); gr.addColorStop(1, 'rgba(0,0,0,0)'); x.globalCompositeOperation = 'multiply'; x.fillStyle = gr; x.fillRect(px + ox - r, py + oy - r, r * 2, r * 2); } }
    x.globalCompositeOperation = 'source-over';
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.minFilter = THREE.LinearMipMapLinearFilter; return t;
  })();
  // Material de piel: color por regiones (pelaje, oscuro, claro, extra), pelo procedural y capas para dar volumen
  function skinMaterial(cols, opt) {
    const m = new THREE.MeshStandardMaterial({ color: '#ffffff', roughness: opt.rough ?? 0.85, metalness: 0 });
    m.skinning = true;
    m.userData.fill = 'shader';
    m.userData.cols = cols;
    m.userData.shell = { value: 0 };
    m.onBeforeCompile = sh => {
      sh.uniforms.cA = { value: cols.coat }; sh.uniforms.cB = { value: cols.dark }; sh.uniforms.cC = { value: cols.light }; sh.uniforms.cD = { value: cols.extra };
      sh.uniforms.shell = m.userData.shell; sh.uniforms.furLen = { value: opt.fur || 0 }; sh.uniforms.furTex = { value: strandTex }; sh.uniforms.furScale = { value: opt.furScale || 9 };
      sh.uniforms.fillK = { value: 0.16 }; sh.uniforms.scaleTex = { value: opt.scales ? 1 : 0 };
      sh.vertexShader = sh.vertexShader
        .replace('#include <common>', '#include <common>\nattribute vec4 rw; attribute float ao; attribute float fm; varying float vAo; varying float vFm; varying vec4 vRw; varying vec3 vRest; varying vec3 vRestN; uniform float shell; uniform float furLen;')
        .replace('#include <begin_vertex>', '#include <begin_vertex>\nvRw = rw; vAo = ao; vFm = fm; vRest = position; vRestN = normal;')
        .replace('#include <skinning_vertex>', '#include <skinning_vertex>\ntransformed += normalize(objectNormal) * shell * furLen * fm;');
      sh.fragmentShader = sh.fragmentShader
        .replace('#include <common>', `#include <common>
varying vec4 vRw; varying float vAo; varying float vFm; varying vec3 vRest; varying vec3 vRestN;
uniform vec3 cA; uniform vec3 cB; uniform vec3 cC; uniform vec3 cD; uniform float shell; uniform float furLen; uniform sampler2D furTex; uniform float furScale; uniform float fillK; uniform float scaleTex;
vec4 tri(vec3 p, vec3 n) { vec3 w = abs(n); w = pow(w, vec3(4.0)); w /= (w.x + w.y + w.z);
  return texture2D(furTex, p.yz * furScale) * w.x + texture2D(furTex, p.xz * furScale) * w.y + texture2D(furTex, p.xy * furScale) * w.z; }`)
        .replace('#include <color_fragment>', `
vec4 rwn = vRw / max(0.001, vRw.x + vRw.y + vRw.z + vRw.w);
vec3 base = cA * rwn.x + cB * rwn.y + cC * rwn.z + cD * rwn.w;
vec4 fz = tri(vRest, normalize(vRestN));
float strand = fz.r;
if (furLen > 0.0 && shell > 0.0) { if (strand < shell * 0.92 + 0.08 || vFm < 0.15 + shell * 0.5) discard; }
float ao = furLen > 0.0 ? mix(0.62, 1.0, shell) : 1.0;
float tone = 0.88 + 0.24 * fz.b + (furLen > 0.0 ? 0.08 * (strand - 0.5) : 0.0);
if (scaleTex > 0.5) { float c = tri(vRest * 1.0, normalize(vRestN)).g; tone *= 0.9 + 0.12 * smoothstep(0.3, 0.7, c); }
diffuseColor.rgb *= base * tone * ao * vAo;`)
        .replace('#include <emissivemap_fragment>', '#include <emissivemap_fragment>\ntotalEmissiveRadiance += diffuseColor.rgb * fillK;');
    };
    return m;
  }
  // Crea la malla con esqueleto y capas de pelo
  function buildSkinned(pack, key, cols, opt) {
    const { geo, head } = decodeModel(pack, key);
    const bones = {}, list = [];
    head.bones.forEach(b => {
      const bone = new THREE.Bone(); bone.name = b.n;
      const pp = b.p ? head.bones.find(x => x.n === b.p).pos : [0, 0, 0];
      bone.position.set(b.pos[0] - pp[0], b.pos[1] - pp[1], b.pos[2] - pp[2]);
      if (b.p) bones[b.p].add(bone);
      bones[b.n] = bone; list.push(bone);
    });
    const skeleton = new THREE.Skeleton(list);
    const mat = skinMaterial(cols, opt);
    const mesh = new THREE.SkinnedMesh(geo, mat); mesh.castShadow = true; mesh.receiveShadow = true;
    mesh.add(list[0]); mesh.bind(skeleton);
    mesh.frustumCulled = false;
    const shells = [];
    if (opt.fur) {
      for (let i = 1; i <= FUR_LAYERS_MAX; i++) {
        const sm = skinMaterial(cols, opt); sm.userData.shell.value = i / FUR_LAYERS_MAX;
        const s = new THREE.SkinnedMesh(geo, sm); s.bind(skeleton); s.frustumCulled = false; s.castShadow = false; s.receiveShadow = true;
        s.userData.layer = i; mesh.add(s); shells.push(s);
      }
    }
    return { mesh, bones, skeleton, shells, anchors: head.anchors, extra: head.extra || {}, mat };
  }
