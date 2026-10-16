  // ---- Personajes con malla esculpida, esqueleto y pelo ----
  const MCFG = {
    dog: { name: 'Salchi', size: 1, speed: 9.5, cols: { coat: '#b9784a', dark: '#7a4a2e', light: '#e3b48d', extra: '#f6a7bf' }, accent: '#f39bbb', fur: 0.022, iris: '#5a3216', eyeR: 0.072, nose: 'dog', collar: 'heart', headBow: [0.0, 0.0, 0, 1.15], tongue: 0.11 },
    cat: { name: 'Miso', size: 1, speed: 10, cols: { coat: '#fffaf7', dark: '#f2e6ea', light: '#ffffff', extra: '#f9b3c7' }, accent: '#f39bbb', fur: 0.04, iris: '#69b4e6', slit: true, eyeR: 0.07, nose: 'cat', neckBow: true, headBow: [-0.06, -0.02, 0.18, 1.0], whiskers: true, tongue: 0.07 },
    rocco: { name: 'Rocco', size: 0.82, speed: 9.5, cols: { coat: '#dcb894', dark: '#c79f78', light: '#fbf7f5', extra: '#f6a7bf' }, accent: '#9fd3f0', fur: 0.016, iris: '#4a2a14', eyeR: 0.07, nose: 'big', collar: 'gold', tongue: 0.1 },
    monkey: { name: 'Samu', size: 0.9, speed: 9.5, cols: { coat: '#8b5a3c', dark: '#5e3b26', light: '#f0cfa8', extra: '#f6a7bf' }, accent: '#f3d36b', fur: 0.026, iris: '#3a2214', eyeR: 0.062, nose: 'monkey', collar: 'plain', tongue: 0.07 },
    turtle: { name: 'DylonBaby30', size: 1, speed: 9.5, cols: { coat: '#7cc576', dark: '#5f7f3e', light: '#e6d79a' }, accent: '#2b2b33', fur: 0, scales: true, white: true, iris: '#2b2420', eyeR: 0.085, nose: null, sash: true, tongue: 0.05 }
  };
  // Medidas del cuerpo esculpido para que los trajes se ajusten
  const MODEL_BODY = {
    dog: { kind: 'cyl', cx: -0.06, cy: 0.8, len: 1.32, r: 0.385, neck: [0.82, 1.1], neckR: 0.28, legR: 0.11 },
    cat: { kind: 'ell', cx: 0, cy: 0.86, rx: 0.72, ry: 0.37, rz: 0.35, neck: [0.62, 1.14], neckR: 0.24, legR: 0.085 },
    rocco: { kind: 'ell', cx: 0.02, cy: 0.9, rx: 0.62, ry: 0.43, rz: 0.43, neck: [0.65, 1.2], neckR: 0.32, legR: 0.13 },
    monkey: { kind: 'ell', cx: 0.02, cy: 0.95, rx: 0.48, ry: 0.42, rz: 0.38, neck: [0.42, 1.27], neckR: 0.25, legR: 0.095 },
    turtle: { kind: 'ell', cx: -0.02, cy: 0.56, rx: 0.64, ry: 0.4, rz: 0.55, neck: [0.6, 0.66], neckR: 0.15, legR: 0.12 }
  };
  const _zf = new THREE.Vector3(0, 0, 1);
  function irisTex(color, slit) {
    const c = document.createElement('canvas'); c.width = c.height = 128; const x = c.getContext('2d'); if (!x) return null;
    const col = new THREE.Color(color).convertLinearToSRGB(), hex = '#' + col.getHexString(), dk = '#' + col.clone().multiplyScalar(0.45).getHexString();
    x.fillStyle = '#1a1012'; x.fillRect(0, 0, 128, 128);
    const g = x.createRadialGradient(64, 64, 8, 64, 64, 60); g.addColorStop(0, hex); g.addColorStop(0.7, hex); g.addColorStop(1, dk);
    x.fillStyle = g; x.beginPath(); x.arc(64, 64, 58, 0, 7); x.fill();
    for (let i = 0; i < 70; i++) { const a = Math.random() * 6.28, r0 = 22 + Math.random() * 10, r1 = 40 + Math.random() * 16; x.strokeStyle = 'rgba(255,255,255,' + (0.06 + Math.random() * 0.1) + ')'; x.lineWidth = 1; x.beginPath(); x.moveTo(64 + Math.cos(a) * r0, 64 + Math.sin(a) * r0); x.lineTo(64 + Math.cos(a) * r1, 64 + Math.sin(a) * r1); x.stroke(); }
    x.fillStyle = '#0b0608'; x.beginPath(); if (slit) x.ellipse(64, 64, 9, 30, 0, 0, 7); else x.arc(64, 64, 22, 0, 7); x.fill();
    x.strokeStyle = 'rgba(0,0,0,.55)'; x.lineWidth = 4; x.beginPath(); x.arc(64, 64, 58, 0, 7); x.stroke();
    const t = new THREE.CanvasTexture(c); t.encoding = THREE.sRGBEncoding; return t;
  }
  function makeEye(cfg) {
    const R = cfg.eyeR, g = new THREE.Group();
    const ball = new THREE.Mesh(new THREE.SphereGeometry(R, 24, 16), new THREE.MeshStandardMaterial({ color: cfg.white ? '#fbfbf8' : '#1a1012', roughness: 0.12 }));
    g.add(ball);
    // Iris pintado como un casquete delante del globo (con su pupila y los reflejos)
    const irisR = cfg.white ? R * 0.55 : R * 0.88;
    const irisGeo = new THREE.SphereGeometry(R * 1.005, 28, 14, 0, Math.PI * 2, 0, Math.asin(irisR / R));
    irisGeo.rotateX(Math.PI / 2);
    // coordenadas de textura planas mirando al frente
    const pa = irisGeo.attributes.position, uv = irisGeo.attributes.uv;
    for (let i = 0; i < pa.count; i++) uv.setXY(i, 0.5 + pa.getX(i) / (irisR * 2), 0.5 + pa.getY(i) / (irisR * 2));
    const iris = new THREE.Mesh(irisGeo, new THREE.MeshStandardMaterial({ map: irisTex(cfg.white ? '#2b2420' : cfg.iris, cfg.slit), roughness: 0.1 }));
    g.add(iris);
    const gl = new THREE.MeshBasicMaterial({ color: '#ffffff' });
    const s1 = new THREE.Mesh(new THREE.SphereGeometry(R * 0.15, 10, 8), gl); s1.position.set(R * 0.3, R * 0.34, R * 0.92); g.add(s1);
    const s2 = new THREE.Mesh(new THREE.SphereGeometry(R * 0.09, 8, 6), gl); s2.position.set(-R * 0.3, -R * 0.3, R * 0.95); g.add(s2);
    [ball, iris].forEach(m => { shinyLater.push(m.material); m.material.userData.fill = false; });
    return g;
  }
  const shinyLater = [];
  function buildModelChar(pack, key, fallback) {
    const cfg = MCFG[key], C0 = cfg.cols;
    const accent = M(cfg.accent, { roughness: 0.45 });
    const cols = { coat: new THREE.Color(C0.coat), dark: new THREE.Color(C0.dark), light: new THREE.Color(C0.light), extra: C0.extra ? new THREE.Color(C0.extra) : accent.color };
    const r = buildSkinned(pack, key, cols, { fur: cfg.fur, furScale: cfg.furScale || 0.6, scales: cfg.scales, rough: cfg.fur ? 0.9 : 0.55 });
    curEyes = [];
    const group = new THREE.Group(); group.add(r.mesh);
    const B = r.bones, body = B.body, head = B.head, A = r.anchors;
    const hp = new THREE.Vector3(), tmp = new THREE.Vector3();
    head.updateWorldMatrix(true, false); hp.setFromMatrixPosition(head.matrixWorld);
    const local = (arr) => new THREE.Vector3().fromArray(arr).sub(hp);
    // Ojos orientados según la superficie de la cara
    ['eyeL', 'eyeR'].forEach(k => {
      if (!A[k]) return;
      const e = makeEye(cfg); e.position.copy(local(A[k].p));
      const n = new THREE.Vector3().fromArray(A[k].n).normalize(); n.y *= 0.5; n.normalize();
      e.quaternion.setFromUnitVectors(_zf, n); head.add(e); e.userData.by = 1; curEyes.push(e);
    });
    // Nariz
    if (cfg.nose && A.nose) {
      const np = local(A.nose.p), nm = M(cfg.nose === 'cat' ? '#f4a3b8' : '#231518', { roughness: 0.22 }); shinyLater.push(nm);
      if (cfg.nose === 'cat') {
        const n = new THREE.Mesh(new THREE.ConeGeometry(0.045, 0.05, 3), nm); n.rotation.z = Math.PI / 2 + 0.25; n.rotation.x = Math.PI / 6; n.scale.set(1, 1.2, 0.8); n.position.copy(np); head.add(n);
      } else if (cfg.nose === 'monkey') {
        [-1, 1].forEach(sd => { const n = new THREE.Mesh(new THREE.SphereGeometry(0.022, 8, 6), nm); n.position.copy(np).add(tmp.set(-0.005, 0.01, 0.035 * sd)); head.add(n); });
      } else {
        const big = cfg.nose === 'big', n = new THREE.Mesh(new THREE.SphereGeometry(big ? 0.085 : 0.07, 18, 12), nm);
        n.scale.set(0.85, 0.72, 1.15); n.position.copy(np).add(tmp.set(-0.02, 0, 0)); head.add(n);
        const nd = M('#0d0708', { roughness: 0.6 });
        [-1, 1].forEach(sd => { const h = new THREE.Mesh(new THREE.SphereGeometry(0.018, 8, 6), nd); h.scale.set(0.6, 0.8, 1); h.position.copy(n.position).add(tmp.set(big ? 0.07 : 0.055, -0.005, 0.03 * sd)); head.add(h); });
        const hl = new THREE.Mesh(new THREE.SphereGeometry(0.016, 8, 6), new THREE.MeshBasicMaterial({ color: '#ffffff' })); hl.position.copy(n.position).add(tmp.set(0.03, 0.045, 0.02)); head.add(hl);
      }
    }
    // Lengua para cuando está contento
    const tongue = new THREE.Mesh(new THREE.SphereGeometry(cfg.tongue, 12, 8), tongueMat);
    tongue.scale.set(1, 0.4, 0.75);
    if (A.nose) tongue.position.copy(local(A.nose.p)).add(tmp.set(-0.12, -0.15, 0)); else tongue.position.set(0.25, -0.12, 0);
    tongue.visible = false; head.add(tongue);
    // Bigotes
    if (cfg.whiskers && A.nose) {
      const wm = M('#e8dfe2', { roughness: 0.5 }), np = local(A.nose.p);
      [-1, 1].forEach(sd => { for (let k = -1; k <= 1; k++) { const w = new THREE.Mesh(new THREE.CylinderGeometry(0.004, 0.006, 0.36, 4), wm); w.position.copy(np).add(tmp.set(-0.08, -0.06 + k * 0.03, 0.17 * sd)); w.rotation.x = Math.PI / 2; w.rotation.z = k * 0.15; w.rotation.y = -0.25 * sd; head.add(w); } });
    }
    // Accesorios de los trajes (corona, flores, gafas)
    const eyeL = A.eyeL ? local(A.eyeL.p) : new THREE.Vector3(0.3, 0.1, 0.2);
    const top = A.top ? local(A.top.p).y : 0.35;
    const acc = addAccessories(head, { top, eyeX: eyeL.x, eyeY: eyeL.y, eyeZ: Math.abs(eyeL.z) + 0.05, r: Math.max(0.24, Math.min(0.38, top * 0.95)) });
    let headBow = null;
    if (cfg.headBow) { const [hx, hy, hz, hs] = cfg.headBow; headBow = makeBow(hs, accent); headBow.position.set(hx - 0.03, top + 0.02 + hy, hz); headBow.rotation.z = hz ? 0.3 : 0; head.add(headBow); }
    // Collar con chapita, lazo al cuello o fajín ninja
    const ex = r.extra || {};
    if (ex.collar && (cfg.collar || cfg.neckBow)) {
      const c = new THREE.Vector3().fromArray(ex.collar[0]), rad = ex.collar[1], dir = hp.clone().sub(c).normalize();
      if (cfg.collar) {
        const tor = new THREE.Mesh(new THREE.TorusGeometry(rad, 0.045, 10, 32), accent); tor.position.copy(c); tor.quaternion.setFromUnitVectors(_zf, dir); body.add(tor);
        const front = new THREE.Vector3(1, 0, 0).sub(dir.clone().multiplyScalar(dir.x)).normalize();
        const tp = c.clone().add(front.multiplyScalar(rad + 0.02)).add(new THREE.Vector3(0, -0.07, 0));
        if (cfg.collar === 'heart') { const h = makeHeart(0.12, M('#f2c94c', { metalness: 0.6, roughness: 0.25 })); h.position.copy(tp); h.rotation.y = Math.PI / 2; body.add(h); }
        else if (cfg.collar === 'gold') { const t = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.06, 0.02, 16), M('#e8b33c', { metalness: 0.6, roughness: 0.3 })); t.rotation.z = Math.PI / 2; t.position.copy(tp); body.add(t); }
      }
      if (cfg.neckBow) { const nb = makeBow(0.9, accent); nb.position.copy(c).add(new THREE.Vector3(0.1, -0.04, 0.22)); body.add(nb); }
    }
    if (cfg.sash) {
      const silver = M('#d9dde3', { metalness: 0.7, roughness: 0.25 });
      const sash = new THREE.Mesh(new THREE.TorusGeometry(0.6, 0.045, 8, 40), accent); sash.rotation.x = Math.PI / 2; sash.scale.set(1.08, 0.94, 1); sash.position.y = 0.5; body.add(sash);
      [-1, 1].forEach(sd => {
        const star = new THREE.Group();
        for (let i = 0; i < 4; i++) { const blade = new THREE.Mesh(new THREE.ConeGeometry(0.04, 0.16, 4), silver); blade.rotation.z = i * Math.PI / 2; blade.position.set(Math.sin(i * Math.PI / 2) * -0.07, Math.cos(i * Math.PI / 2) * 0.07, 0); star.add(blade); }
        star.position.set(-0.05, 0.52, 0.6 * sd); star.rotation.y = sd > 0 ? 0 : Math.PI; body.add(star);
      });
    }
    // Patas: hueso de cada pata con su fase de paso
    const legs = ['legFL', 'legFR', 'legBL', 'legBR'].map((n, i) => {
      const b = B[n]; b.updateWorldMatrix(true, false); const wp = new THREE.Vector3().setFromMatrixPosition(b.matrixWorld);
      b.userData.phase = (i === 0 || i === 3) ? 0 : Math.PI; b.userData.footY = 0.06 - wp.y; return b;
    });
    const ears = ['earL', 'earR'].filter(n => B[n]).map(n => { B[n].userData.side = n === 'earL' ? 1 : -1; return B[n]; });
    group.scale.setScalar(CHAR_SCALE);
    return {
      size: cfg.size, name: cfg.name, group, body, head, legs, ears, tailWag: B.tail || new THREE.Object3D(), tongue, hurtMat: r.mat, reach: 0.95, speed: cfg.speed,
      mats: { coat: { color: cols.coat }, dark: { color: cols.dark }, light: { color: cols.light }, accent }, acc, headBow, eyes: curEyes, noFur: true, model: true, shells: r.shells, furLen: cfg.fur
    };
  }
  // Muestra n capas de pelo repartidas a lo largo de su longitud
  function setFur(C, n) {
    if (!C.shells || C._furN === n) return; C._furN = n;
    const vis = new Set(); for (let j = 1; j <= n; j++) vis.add(Math.round(j * FUR_LAYERS_MAX / n));
    C.shells.forEach(s => { s.visible = vis.has(s.userData.layer); });
  }
