/* pkushal.com.np - interactive centerpiece graph (three.js).
   A bright, grab-and-spin link graph. Drag to rotate (with inertia), auto-rotates
   when idle, and highlights the node under the pointer. Guarded and idle-loaded. */
(function () {
  var canvas = document.getElementById('graph3d');
  if (!canvas) return;
  if (window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  try {
    var probe = document.createElement('canvas');
    if (!(probe.getContext('webgl') || probe.getContext('experimental-webgl'))) return;
  } catch (e) { return; }

  function start() {
    import('https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js')
      .then(init).catch(function () { });
  }

  function dot(THREE) {
    var c = document.createElement('canvas'); c.width = c.height = 64;
    var g = c.getContext('2d');
    var grd = g.createRadialGradient(32, 32, 0, 32, 32, 32);
    grd.addColorStop(0, 'rgba(255,255,255,1)');
    grd.addColorStop(0.28, 'rgba(160,220,255,1)');
    grd.addColorStop(1, 'rgba(160,220,255,0)');
    g.fillStyle = grd; g.beginPath(); g.arc(32, 32, 32, 0, Math.PI * 2); g.fill();
    var tx = new THREE.CanvasTexture(c); tx.needsUpdate = true; return tx;
  }

  function init(THREE) {
    var mobile = Math.min(window.innerWidth, window.innerHeight) < 700;
    var COUNT = mobile ? 84 : 150, LINK = mobile ? 40 : 34;
    var W = canvas.clientWidth || 1, H = canvas.clientHeight || 1;

    var renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: !mobile, powerPreference: 'low-power' });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, mobile ? 1.25 : 1.75));
    renderer.setSize(W, H, false);

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(52, W / H, 1, 1000);
    camera.position.z = 142;
    var group = new THREE.Group(); scene.add(group);

    var sprite = dot(THREE);
    var R = mobile ? 84 : 94, pos = new Float32Array(COUNT * 3), base = [];
    for (var i = 0; i < COUNT; i++) {
      var u = Math.random(), v = Math.random(), th = 2 * Math.PI * u, ph = Math.acos(2 * v - 1);
      var r = R * Math.cbrt(Math.random());
      var x = r * Math.sin(ph) * Math.cos(th), y = r * Math.sin(ph) * Math.sin(th), z = r * Math.cos(ph);
      pos[i * 3] = x; pos[i * 3 + 1] = y; pos[i * 3 + 2] = z;
      base.push({ x: x, y: y, z: z, px: Math.random() * 6.28, py: Math.random() * 6.28, s: 0.4 + Math.random() * 0.8 });
    }
    var pgeo = new THREE.BufferGeometry();
    pgeo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    pgeo.boundingSphere = new THREE.Sphere(new THREE.Vector3(0, 0, 0), R + 24);
    var pmat = new THREE.PointsMaterial({
      size: mobile ? 3.6 : 3.3, map: sprite, transparent: true, color: 0xbfe8ff,
      depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true, opacity: 1
    });
    var points = new THREE.Points(pgeo, pmat); group.add(points);

    var segs = [];
    for (var a = 0; a < COUNT; a++) for (var b = a + 1; b < COUNT; b++) {
      var dx = base[a].x - base[b].x, dy = base[a].y - base[b].y, dz = base[a].z - base[b].z;
      if (dx * dx + dy * dy + dz * dz < LINK * LINK) segs.push(a, b);
    }
    var lpos = new Float32Array(segs.length * 3);
    var lgeo = new THREE.BufferGeometry();
    lgeo.setAttribute('position', new THREE.BufferAttribute(lpos, 3));
    var lmat = new THREE.LineBasicMaterial({ color: 0x4a97c7, transparent: true, opacity: 0.6, blending: THREE.AdditiveBlending, depthWrite: false });
    group.add(new THREE.LineSegments(lgeo, lmat));

    var hl = new THREE.Sprite(new THREE.SpriteMaterial({ map: sprite, color: 0xffffff, transparent: true, opacity: 0.95, blending: THREE.AdditiveBlending, depthWrite: false }));
    hl.scale.set(11, 11, 1); hl.visible = false; group.add(hl);

    var ray = new THREE.Raycaster(); ray.params.Points.threshold = 4.2;
    var ndc = new THREE.Vector2(), hasPtr = false;
    var rotX = 0.22, rotY = 0, velX = 0, velY = 0, dragging = false, lx = 0, ly = 0;

    canvas.addEventListener('pointerdown', function (e) {
      dragging = true; lx = e.clientX; ly = e.clientY;
      try { canvas.setPointerCapture(e.pointerId); } catch (x) { }
    });
    canvas.addEventListener('pointermove', function (e) {
      var rect = canvas.getBoundingClientRect();
      ndc.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      ndc.y = -((e.clientY - rect.top) / rect.height) * 2 + 1; hasPtr = true;
      if (dragging) {
        var dx = e.clientX - lx, dy = e.clientY - ly;
        rotY += dx * 0.006; rotX += dy * 0.006;
        rotX = Math.max(-1.2, Math.min(1.2, rotX));
        velY = dx * 0.006; velX = dy * 0.006; lx = e.clientX; ly = e.clientY;
      }
    });
    function endDrag() { dragging = false; }
    canvas.addEventListener('pointerup', endDrag);
    canvas.addEventListener('pointercancel', endDrag);
    canvas.addEventListener('pointerleave', function () { hasPtr = false; endDrag(); });

    var t0 = performance.now(), running = true, raf = 0, parr = pgeo.attributes.position.array;
    function frame(now) {
      if (!running) return;
      var t = (now - t0) * 0.001;
      for (var i = 0; i < COUNT; i++) {
        var bb = base[i];
        parr[i * 3]     = bb.x + Math.sin(t * 0.28 + bb.px) * 2.4 * bb.s;
        parr[i * 3 + 1] = bb.y + Math.cos(t * 0.24 + bb.py) * 2.4 * bb.s;
        parr[i * 3 + 2] = bb.z + Math.sin(t * 0.2 + bb.px) * 2.0 * bb.s;
      }
      pgeo.attributes.position.needsUpdate = true;
      for (var s = 0; s < segs.length; s += 2) {
        var ia = segs[s] * 3, ib = segs[s + 1] * 3, o = (s / 2) * 6;
        lpos[o] = parr[ia]; lpos[o + 1] = parr[ia + 1]; lpos[o + 2] = parr[ia + 2];
        lpos[o + 3] = parr[ib]; lpos[o + 4] = parr[ib + 1]; lpos[o + 5] = parr[ib + 2];
      }
      lgeo.attributes.position.needsUpdate = true;

      if (!dragging) { rotY += velY + 0.0018; rotX += velX; velX *= 0.93; velY *= 0.93; }
      group.rotation.x = rotX; group.rotation.y = rotY;

      if (hasPtr) {
        ray.setFromCamera(ndc, camera);
        var hit = ray.intersectObject(points);
        if (hit.length) {
          var idx = hit[0].index;
          hl.position.set(parr[idx * 3], parr[idx * 3 + 1], parr[idx * 3 + 2]);
          hl.visible = true;
        } else hl.visible = false;
      } else hl.visible = false;

      renderer.render(scene, camera);
      raf = requestAnimationFrame(frame);
    }
    function play() { if (!running) { running = true; t0 = performance.now(); } cancelAnimationFrame(raf); raf = requestAnimationFrame(frame); }
    function stop() { running = false; cancelAnimationFrame(raf); }
    raf = requestAnimationFrame(frame);

    function resize() {
      W = canvas.clientWidth || 1; H = canvas.clientHeight || 1;
      camera.aspect = W / H; camera.updateProjectionMatrix();
      renderer.setSize(W, H, false);
    }
    window.addEventListener('resize', resize, { passive: true });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (en) {
        en.forEach(function (x) { if (x.isIntersecting) play(); else stop(); });
      }, { threshold: 0.05 }).observe(canvas);
    }
    document.addEventListener('visibilitychange', function () { if (document.hidden) stop(); else play(); });
  }

  if ('requestIdleCallback' in window) requestIdleCallback(start, { timeout: 2800 });
  else setTimeout(start, 1800);
})();
