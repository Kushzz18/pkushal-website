/* pkushal.com.np - hero constellation (three.js).
   Progressive and optional: it never blocks first paint and degrades to nothing
   on reduced-motion, no-WebGL, or if the CDN import fails. Loaded after idle. */
(function () {
  var canvas = document.getElementById('bg3d');
  if (!canvas) return;
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  try {
    var probe = document.createElement('canvas');
    if (!(probe.getContext('webgl') || probe.getContext('experimental-webgl'))) return;
  } catch (e) { return; }

  function start() {
    import('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js')
      .then(init)
      .catch(function () { /* background is optional; stay silent */ });
  }

  function makeDot(THREE) {
    var c = document.createElement('canvas'); c.width = c.height = 64;
    var g = c.getContext('2d');
    var grd = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    grd.addColorStop(0, 'rgba(255,255,255,1)');
    grd.addColorStop(0.25, 'rgba(150,214,255,1)');
    grd.addColorStop(1, 'rgba(150,214,255,0)');
    g.fillStyle = grd; g.beginPath(); g.arc(32, 32, 32, 0, Math.PI * 2); g.fill();
    var tx = new THREE.CanvasTexture(c); tx.needsUpdate = true; return tx;
  }

  function init(THREE) {
    var mobile = Math.min(window.innerWidth, window.innerHeight) < 700;
    var COUNT = mobile ? 66 : 150;
    var LINK = mobile ? 32 : 30;
    var W = canvas.clientWidth || 1, H = canvas.clientHeight || 1;

    var renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: !mobile, powerPreference: 'low-power' });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, mobile ? 1 : 1.5));
    renderer.setSize(W, H, false);

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(55, W / H, 1, 1000);
    camera.position.z = 122;
    var group = new THREE.Group(); scene.add(group);

    var R = 80, pos = new Float32Array(COUNT * 3), base = [];
    for (var i = 0; i < COUNT; i++) {
      var u = Math.random(), v = Math.random(), th = 2 * Math.PI * u, ph = Math.acos(2 * v - 1);
      var r = R * Math.cbrt(Math.random());
      var x = r * Math.sin(ph) * Math.cos(th),
          y = r * Math.sin(ph) * Math.sin(th) * 0.82,
          z = r * Math.cos(ph) * 0.6;
      pos[i * 3] = x; pos[i * 3 + 1] = y; pos[i * 3 + 2] = z;
      base.push({ x: x, y: y, z: z, px: Math.random() * 6.28, py: Math.random() * 6.28, s: 0.4 + Math.random() * 0.8 });
    }
    var pgeo = new THREE.BufferGeometry();
    pgeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    var pmat = new THREE.PointsMaterial({
      size: mobile ? 2.7 : 2.2, map: makeDot(THREE), transparent: true, color: 0x9bd8ff,
      depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true, opacity: 0.92
    });
    group.add(new THREE.Points(pgeo, pmat));

    var segs = [];
    for (var a = 0; a < COUNT; a++) for (var b = a + 1; b < COUNT; b++) {
      var dx = base[a].x - base[b].x, dy = base[a].y - base[b].y, dz = base[a].z - base[b].z;
      if (dx * dx + dy * dy + dz * dz < LINK * LINK) segs.push(a, b);
    }
    var lpos = new Float32Array(segs.length * 3);
    var lgeo = new THREE.BufferGeometry();
    lgeo.setAttribute('position', new THREE.BufferAttribute(lpos, 3));
    var lmat = new THREE.LineBasicMaterial({ color: 0x2f6f96, transparent: true, opacity: 0.5, blending: THREE.AdditiveBlending, depthWrite: false });
    group.add(new THREE.LineSegments(lgeo, lmat));

    var mx = 0, my = 0, tmx = 0, tmy = 0;
    window.addEventListener('pointermove', function (e) {
      tmx = e.clientX / window.innerWidth - 0.5;
      tmy = e.clientY / window.innerHeight - 0.5;
    }, { passive: true });

    var t0 = performance.now(), running = true, raf = 0, parr = pgeo.attributes.position.array;
    function frame(now) {
      if (!running) return;
      var t = (now - t0) * 0.001;
      for (var i = 0; i < COUNT; i++) {
        var bb = base[i];
        parr[i * 3]     = bb.x + Math.sin(t * 0.25 + bb.px) * 3.2 * bb.s;
        parr[i * 3 + 1] = bb.y + Math.cos(t * 0.22 + bb.py) * 3.2 * bb.s;
        parr[i * 3 + 2] = bb.z + Math.sin(t * 0.18 + bb.px) * 2.4 * bb.s;
      }
      pgeo.attributes.position.needsUpdate = true;
      for (var s = 0; s < segs.length; s += 2) {
        var ia = segs[s] * 3, ib = segs[s + 1] * 3, o = (s / 2) * 6;
        lpos[o] = parr[ia]; lpos[o + 1] = parr[ia + 1]; lpos[o + 2] = parr[ia + 2];
        lpos[o + 3] = parr[ib]; lpos[o + 4] = parr[ib + 1]; lpos[o + 5] = parr[ib + 2];
      }
      lgeo.attributes.position.needsUpdate = true;
      mx += (tmx - mx) * 0.04; my += (tmy - my) * 0.04;
      group.rotation.y = t * 0.06 + mx * 0.6;
      group.rotation.x = my * 0.5;
      renderer.render(scene, camera);
      raf = requestAnimationFrame(frame);
    }
    function play() { if (!running) { running = true; t0 = performance.now() - 0; } cancelAnimationFrame(raf); raf = requestAnimationFrame(frame); }
    function stop() { running = false; cancelAnimationFrame(raf); }
    raf = requestAnimationFrame(frame);

    window.addEventListener('resize', function () {
      W = canvas.clientWidth || 1; H = canvas.clientHeight || 1;
      camera.aspect = W / H; camera.updateProjectionMatrix();
      renderer.setSize(W, H, false);
    }, { passive: true });

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) {
        en.forEach(function (x) { if (x.isIntersecting) play(); else stop(); });
      }, { threshold: 0.02 }).observe(canvas);
    }
    document.addEventListener('visibilitychange', function () { if (document.hidden) stop(); else play(); });
  }

  if ('requestIdleCallback' in window) requestIdleCallback(start, { timeout: 2600 });
  else setTimeout(start, 1600);
})();
