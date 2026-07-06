// ── LENIS SMOOTH MOMENTUM SCROLL ──
const lenis = new Lenis({
  duration: 2.2, // Ultra smooth & heavy
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  direction: 'vertical',
  gestureDirection: 'vertical',
  smooth: true,
  mouseMultiplier: 1.0,
  smoothTouch: false,
  touchMultiplier: 1.5,
  infinite: false,
});

function raf(time) {
  lenis.raf(time);
  requestAnimationFrame(raf);
}
requestAnimationFrame(raf);

gsap.registerPlugin(ScrollTrigger);
lenis.on('scroll', ScrollTrigger.update);
ScrollTrigger.scrollerProxy(document.body, {
  scrollTop(value) {
    return arguments.length ? lenis.scrollTo(value, { immediate: true }) : lenis.scroll;
  },
  getBoundingClientRect() {
    return { top: 0, left: 0, width: window.innerWidth, height: window.innerHeight };
  }
});
ScrollTrigger.addEventListener('refresh', () => lenis.resize());
ScrollTrigger.refresh();

// ── CUSTOM MAGNETIC CURSOR ──
const cursor = document.getElementById('custom-cursor');
const cursorDot = cursor.querySelector('.cursor-dot');

let mouse = { x: 0, y: 0 };
let dotPos = { x: 0, y: 0 };

window.addEventListener('mousemove', (e) => {
  mouse.x = e.clientX;
  mouse.y = e.clientY;
});

function updateCursor() {
  dotPos.x += (mouse.x - dotPos.x) * 0.15;
  dotPos.y += (mouse.y - dotPos.y) * 0.15;
  cursorDot.style.left = `${dotPos.x}px`;
  cursorDot.style.top = `${dotPos.y}px`;
  requestAnimationFrame(updateCursor);
}
requestAnimationFrame(updateCursor);

document.querySelectorAll('a, button, .upload-zone').forEach(el => {
  el.addEventListener('mouseenter', () => cursor.classList.add('hover-btn'));
  el.addEventListener('mouseleave', () => cursor.classList.remove('hover-btn'));
});

// ── PRELOADER ──
const preloader = document.getElementById('preloader');
const preloaderPercent = document.getElementById('preloader-percent');
const preloaderFill = document.getElementById('preloader-fill');
const preloaderBar = document.getElementById('preloader-bar');

let loadVal = 0;
const loadInterval = setInterval(() => {
  loadVal += Math.floor(Math.random() * 8) + 2;
  if (loadVal >= 100) {
    loadVal = 100;
    clearInterval(loadInterval);
    triggerWebsiteReveal();
  }
  
  preloaderPercent.textContent = `${loadVal.toString().padStart(2, '0')}%`;
  preloaderFill.style.clipPath = `polygon(0 ${100 - loadVal}%, 100% ${100 - loadVal}%, 100% 100%, 0 100%)`;
  preloaderBar.style.width = `${loadVal}%`;
  
}, 60);

function triggerWebsiteReveal() {
  const tl = gsap.timeline();
  
  tl.to('.preloader-wrapper, .preloader-bottom', { opacity: 0, y: -30, duration: 0.8, ease: "power2.inOut" });
  tl.to(preloader, { 
    yPercent: -100, 
    duration: 1.4, 
    ease: "power4.inOut",
    onComplete: () => {
      document.body.classList.remove('loading');
      ScrollTrigger.refresh();
    }
  }, "-=0.2");

  // Hero Reveal
  tl.fromTo('.hero-title .line-wrap span', 
    { y: "110%" }, 
    { y: "0%", duration: 1.6, stagger: 0.1, ease: "power4.out" }, "-=0.6"
  );
  
  tl.fromTo('.reveal-fade', 
    { opacity: 0, y: 30 }, 
    { opacity: 1, y: 0, duration: 1.5, stagger: 0.15, ease: "power3.out" }, "-=1.2"
  );
  
  tl.fromTo('.reveal-clip',
    { clipPath: 'polygon(0 100%, 100% 100%, 100% 100%, 0 100%)' },
    { clipPath: 'polygon(0 0%, 100% 0%, 100% 100%, 0 100%)', duration: 1.6, stagger: 0.1, ease: "power4.inOut" }, "-=1.5"
  );
}

// ── GSAP SCROLL ANIMATIONS ──
gsap.utils.toArray('.reveal-fade:not(.hero-subtitle)').forEach(section => {
  gsap.fromTo(section, { opacity: 0, y: 60 }, {
    opacity: 1, y: 0, duration: 1.5, ease: "power3.out",
    scrollTrigger: {
      trigger: section,
      start: "top bottom-=100px",
      once: true
    }
  });
});

gsap.utils.toArray('.reveal-clip:not(.hero-img-wrap)').forEach(section => {
  gsap.fromTo(section, { clipPath: 'polygon(0 100%, 100% 100%, 100% 100%, 0 100%)' }, {
    clipPath: 'polygon(0 0%, 100% 0%, 100% 100%, 0 100%)', duration: 1.5, ease: "power4.inOut",
    scrollTrigger: {
      trigger: section,
      start: "top bottom-=100px",
      once: true
    }
  });
});

gsap.utils.toArray('.parallax-img-wrap').forEach(wrap => {
  const img = wrap.querySelector('.parallax-img');
  if(img) {
    gsap.to(img, {
      yPercent: 30, // heavy parallax
      ease: "none",
      scrollTrigger: {
        trigger: wrap,
        start: "top bottom",
        end: "bottom top",
        scrub: true
      }
    });
  }
});

// Marquee Animation
gsap.to('.marquee-track', {
  xPercent: -50,
  ease: "none",
  scrollTrigger: {
    trigger: ".marquee-section",
    start: "top bottom",
    end: "bottom top",
    scrub: true
  }
});


// ── WEBGL ORGANIC FLUID SHADER (THREE.JS) ──
const canvas = document.getElementById('webgl-canvas');
if(canvas && THREE) {
  const scene = new THREE.Scene();
  const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
  const renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);

  const geometry = new THREE.PlaneGeometry(2, 2);
  const material = new THREE.ShaderMaterial({
    uniforms: {
      u_time: { value: 0.0 },
      u_resolution: { value: new THREE.Vector2(window.innerWidth, window.innerHeight) },
      u_mouse: { value: new THREE.Vector2(0, 0) },
      u_scroll: { value: 0 }
    },
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float u_time;
      uniform vec2 u_resolution;
      uniform vec2 u_mouse;
      uniform float u_scroll;
      varying vec2 vUv;
      
      // Simplex noise
      vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
      vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
      vec3 permute(vec3 x) { return mod289(((x*34.0)+1.0)*x); }
      float snoise(vec2 v) {
        const vec4 C = vec4(0.211324865405187, 0.366025403784439, -0.577350269189626, 0.024390243902439);
        vec2 i  = floor(v + dot(v, C.yy) );
        vec2 x0 = v -   i + dot(i, C.xx);
        vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
        vec4 x12 = x0.xyxy + C.xxzz;
        x12.xy -= i1;
        i = mod289(i);
        vec3 p = permute( permute( i.y + vec3(0.0, i1.y, 1.0 )) + i.x + vec3(0.0, i1.x, 1.0 ));
        vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy), dot(x12.zw,x12.zw)), 0.0);
        m = m*m; m = m*m;
        vec3 x = 2.0 * fract(p * C.www) - 1.0;
        vec3 h = abs(x) - 0.5;
        vec3 ox = floor(x + 0.5);
        vec3 a0 = x - ox;
        m *= 1.79284291400159 - 0.85373472095314 * ( a0*a0 + h*h );
        vec3 g;
        g.x  = a0.x  * x0.x  + h.x  * x0.y;
        g.yz = a0.yz * x12.xz + h.yz * x12.yw;
        return 130.0 * dot(m, g);
      }

      void main() {
        vec2 st = gl_FragCoord.xy/u_resolution.xy;
        st.x *= u_resolution.x/u_resolution.y;

        // Mouse influence
        vec2 mouse = u_mouse / u_resolution;
        float dist = distance(st, vec2(mouse.x * (u_resolution.x/u_resolution.y), 1.0 - mouse.y));
        float mouseEffect = smoothstep(0.5, 0.0, dist) * 0.5;

        vec2 pos = vec2(st*3.0);
        
        float n = snoise(pos - u_time * 0.1 + u_scroll * 0.001);
        float n2 = snoise(pos + vec2(n) - u_time * 0.15);
        
        // Dark rich colors: #0A0908 (10,9,8) and #1A1510
        vec3 color1 = vec3(0.039, 0.035, 0.031);
        vec3 color2 = vec3(0.102, 0.082, 0.063);
        
        float mixVal = smoothstep(-1.0, 1.0, n2 + mouseEffect);
        vec3 finalColor = mix(color1, color2, mixVal);
        
        gl_FragColor = vec4(finalColor, 1.0);
      }
    `
  });

  const mesh = new THREE.Mesh(geometry, material);
  scene.add(mesh);

  window.addEventListener('resize', () => {
    renderer.setSize(window.innerWidth, window.innerHeight);
    material.uniforms.u_resolution.value.set(window.innerWidth, window.innerHeight);
  });

  window.addEventListener('mousemove', (e) => {
    material.uniforms.u_mouse.value.set(e.clientX, e.clientY);
  });

  let time = 0;
  function animateWebGL() {
    time += 0.01;
    material.uniforms.u_time.value = time;
    material.uniforms.u_scroll.value = window.scrollY;
    renderer.render(scene, camera);
    requestAnimationFrame(animateWebGL);
  }
  animateWebGL();
}


// ── IMAGE UPLOAD & INFERENCE ──
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const previewBox = document.getElementById('preview-box');
const imagePreview = document.getElementById('image-preview');
const btnRemoveFile = document.getElementById('btn-remove-file');
const btnRunInference = document.getElementById('btn-run-inference');
const emptyStateOutputs = document.getElementById('empty-state-outputs');
const outputDataBox = document.getElementById('output-data-box');

let currentFile = null;

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.style.borderColor = 'var(--text-primary)';
});
dropZone.addEventListener('dragleave', () => {
  dropZone.style.borderColor = 'var(--border-focus)';
});
dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.style.borderColor = 'var(--border-focus)';
  if (e.dataTransfer.files.length) validateAndLoadFile(e.dataTransfer.files[0]);
});

fileInput.addEventListener('change', () => {
  if (fileInput.files.length) validateAndLoadFile(fileInput.files[0]);
});

function validateAndLoadFile(file) {
  if (!file.type.startsWith('image/')) {
    alert('Please select a valid image.');
    return;
  }
  currentFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    imagePreview.src = e.target.result;
    dropZone.style.display = 'none';
    previewBox.style.display = 'block';
    btnRunInference.disabled = false;
    emptyStateOutputs.style.display = 'flex';
    outputDataBox.style.display = 'none';
  };
  reader.readAsDataURL(file);
}

btnRemoveFile.addEventListener('click', () => {
  currentFile = null;
  fileInput.value = '';
  previewBox.style.display = 'none';
  dropZone.style.display = 'block';
  btnRunInference.disabled = true;
  emptyStateOutputs.style.display = 'flex';
  outputDataBox.style.display = 'none';
});

btnRunInference.addEventListener('click', () => {
  if (!currentFile) return;
  const btnText = btnRunInference.querySelector('.btn-inner-text');
  btnText.textContent = "Synthesizing...";
  btnRunInference.disabled = true;
  
  const startTime = performance.now();
  const formData = new FormData();
  formData.append('file', currentFile);
  
  fetch('/predict', { method: 'POST', body: formData })
  .then(res => res.json())
  .then(data => {
    const latency = ((performance.now() - startTime) / 1000).toFixed(2);
    if (data.error) { alert(`Error: ${data.error}`); return; }
    
    emptyStateOutputs.style.display = 'none';
    outputDataBox.style.display = 'flex';
    
    document.getElementById('res-bengali-text').textContent = data.bengali;
    document.getElementById('res-english-text').textContent = data.english || "(No translation generated)";
    document.getElementById('conf-text-val').textContent = `${data.confidence}%`;
    document.getElementById('res-latency').textContent = `${latency}s`;
    
    const warningEl = document.getElementById('res-engine-warning');
    if (data.warning) {
      warningEl.textContent = `Note: ${data.warning}`;
      warningEl.style.display = 'block';
    } else {
      warningEl.style.display = 'none';
    }
    
    lenis.scrollTo(outputDataBox, { offset: -100, duration: 2.0 });
  })
  .catch(err => alert(`Failed: ${err.message}`))
  .finally(() => {
    btnText.textContent = "Synthesize";
    btnRunInference.disabled = false;
  });
});

// ── AUDIO SYNTHESIS ──
const audioCache = { bn: null, en: null };

document.getElementById('btn-tts-bengali').addEventListener('click', () => {
  speakText(document.getElementById('res-bengali-text').textContent, 'bn');
});

document.getElementById('btn-tts-english').addEventListener('click', () => {
  speakText(document.getElementById('res-english-text').textContent, 'en');
});

function speakText(text, lang) {
  if (!text) return;
  if (audioCache[lang]) { new Audio(audioCache[lang]).play(); return; }
  
  fetch('/synthesize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text, lang })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) throw new Error(data.error);
    audioCache[lang] = data.audio_url;
    new Audio(data.audio_url).play();
  })
  .catch(err => alert(`Audio error: ${err.message}`));
}
