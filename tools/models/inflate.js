  // Descompresor DEFLATE pequeñito (para los modelos 3D incrustados en la página)
  function inflateRaw(src) {
    let out = new Uint8Array(src.length * 4), op = 0, bp = 0, bb = 0, bc = 0;
    const need = n => { if (op + n > out.length) { const o2 = new Uint8Array(Math.max(out.length * 2, op + n)); o2.set(out); out = o2; } };
    const bit = () => { if (!bc) { bb = src[bp++]; bc = 8; } const b = bb & 1; bb >>= 1; bc--; return b; };
    const bits = n => { let v = 0; for (let i = 0; i < n; i++) v |= bit() << i; return v; };
    function tree(lens) {
      const cnt = new Uint16Array(16), offs = new Uint16Array(16), sym = new Uint16Array(lens.length);
      for (let i = 0; i < lens.length; i++) cnt[lens[i]]++;
      cnt[0] = 0;
      for (let i = 1; i < 16; i++) offs[i] = offs[i - 1] + cnt[i - 1];
      for (let i = 0; i < lens.length; i++) if (lens[i]) sym[offs[lens[i]]++] = i;
      return { cnt, sym };
    }
    function dec(t) {
      let code = 0, first = 0, idx = 0;
      for (let len = 1; len < 16; len++) {
        code |= bit(); const c = t.cnt[len];
        if (code - c < first) return t.sym[idx + code - first];
        idx += c; first += c; first <<= 1; code <<= 1;
      }
      throw new Error('inflate');
    }
    const LB = [3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 15, 17, 19, 23, 27, 31, 35, 43, 51, 59, 67, 83, 99, 115, 131, 163, 195, 227, 258];
    const LE = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 0];
    const DB = [1, 2, 3, 4, 5, 7, 9, 13, 17, 25, 33, 49, 65, 97, 129, 193, 257, 385, 513, 769, 1025, 1537, 2049, 3073, 4097, 6145, 8193, 12289, 16385, 24577];
    const DE = [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 12, 13, 13];
    let fixL = null, fixD = null;
    let last = 0;
    while (!last) {
      last = bit(); const type = bits(2);
      if (type === 0) {
        bc = 0; const len = src[bp] | (src[bp + 1] << 8); bp += 4;
        need(len); out.set(src.subarray(bp, bp + len), op); op += len; bp += len;
        continue;
      }
      let lt, dt;
      if (type === 1) {
        if (!fixL) { const l = new Uint8Array(288); l.fill(8, 0, 144); l.fill(9, 144, 256); l.fill(7, 256, 280); l.fill(8, 280, 288); fixL = tree(l); fixD = tree(new Uint8Array(30).fill(5)); }
        lt = fixL; dt = fixD;
      } else {
        const hl = bits(5) + 257, hd = bits(5) + 1, hc = bits(4) + 4;
        const ord = [16, 17, 18, 0, 8, 7, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 15], cl = new Uint8Array(19);
        for (let i = 0; i < hc; i++) cl[ord[i]] = bits(3);
        const ct = tree(cl), lens = new Uint8Array(hl + hd);
        for (let i = 0; i < hl + hd;) {
          const s = dec(ct);
          if (s < 16) lens[i++] = s;
          else if (s === 16) { const p = lens[i - 1], r = 3 + bits(2); for (let k = 0; k < r; k++) lens[i++] = p; }
          else if (s === 17) { i += 3 + bits(3); }
          else { i += 11 + bits(7); }
        }
        lt = tree(lens.subarray(0, hl)); dt = tree(lens.subarray(hl));
      }
      for (;;) {
        const s = dec(lt);
        if (s < 256) { need(1); out[op++] = s; }
        else if (s === 256) break;
        else {
          const li = s - 257, len = LB[li] + bits(LE[li]);
          const di = dec(dt), dist = DB[di] + bits(DE[di]);
          need(len);
          for (let k = 0; k < len; k++, op++) out[op] = out[op - dist];
        }
      }
    }
    return out.subarray(0, op);
  }
