/* patlau.com — site behaviour (hero rotation, nav/progress rail, lightbox, sticky banner, music, contact, compare, video).
   Moved out of inline <script> blocks so a strict Content-Security-Policy (script-src 'self') can be used. */
(function(){
  var banner = document.querySelector('.banner');
  function sync(){
    if(!banner) return;
    var h = banner.offsetHeight;
    document.documentElement.style.setProperty('--bar-h', h + 'px');
  }
  window.addEventListener('resize', sync);
  window.addEventListener('load', sync);
  if (document.readyState !== 'loading') sync();
  else document.addEventListener('DOMContentLoaded', sync);
  // re-measure after fonts/images settle the banner height
  setTimeout(sync, 300); setTimeout(sync, 1000);
})();
/* SPLASH — Web Animations API on two recycled divs.
   No transition:none, no rAF, no reflow. element.animate() commits the
   first keyframe natively at the compositor — eliminates the snap.
   Previous fill:forwards animations are cancelled before each new cycle. */
(function(){
  var front = document.getElementById('splashA');
  var back  = document.getElementById('splashB');
  var imgs=[], idx=0;

  function pad(n){ return (n<10?'0':'')+n; }
  function url(n){ return '/splash'+pad(n)+'.jpg'; }
  // 21 splash frames ship with the site; list them explicitly (no 404-probing).
  var SPLASH_COUNT=21;
  for(var i=1;i<=SPLASH_COUNT;i++) imgs.push(url(i));
  var REDUCE = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var motion = {
    1:'zin',  2:'zctr', 3:'zin',  4:'pantop',
    5:'zout', 6:'zin',  7:'zout', 8:'pantop',
    9:'lr',   10:'alt_zlr', 11:'zin', 12:'travY',
    13:'zin', 14:'zout', 15:'zin', 16:'zpt',
    17:'travY',18:'zout', 19:'zpt', 20:'zpt'
  };
  var toggle={};
  var MOTION_DUR=13000, FADE=2000;
  var anims = new Map();   // div -> [animation,...] for cancellation

  function tfPair(n){
    var m = motion[n] || 'zin';
    var t = toggle[n]||0; toggle[n]=t+1;
    if(m==='alt_zlr'){ m = (t%2===0) ? (t%4===0?'zin':'zout') : 'lr'; }
    // transform-origin is center-top (default), so scale expands downward from the top edge:
    // the TOP of the image stays pinned through every zoom.
    if(m==='zin')  return ['scale(1.0)','scale(1.12)'];   // zoom in, top pinned
    if(m==='zout') return ['scale(1.12)','scale(1.0)'];   // zoom out, top pinned
    if(m==='zctr') return ['scale(1.0)','scale(1.12)'];   // splash02: zoom in, centered origin
    if(m==='zpt')  return ['scale(1.0)','scale(1.18)'];   // zoom INTO a focal point (a bit deeper)
    // vertical pans (origin top): translateY 0 = top flush; negative reveals lower.
    if(m==='up')   return ['scale(1.12) translateY(0%)','scale(1.12) translateY(-3%)'];   // start at top
    if(m==='down') return ['scale(1.12) translateY(-3%)','scale(1.12) translateY(0%)'];   // end at top
    if(m==='dnbot')return ['scale(1.12) translateY(0%)','scale(1.12) translateY(-4%)'];
    // pantop (04,08): near-square images. Scale up MORE (1.22) to create vertical overscan,
    // then pan a clearly visible amount, ENDING at the top (translateY 0 = top flush).
    if(m==='pantop')return ['scale(1.22) translateY(-7%)','scale(1.22) translateY(0%)'];
    // travY (12,17): full traverse — start showing bottom, end showing top (or vice versa each cycle).
    if(m==='travY'){
      return (t%2===0)
        ? ['scale(1.22) translateY(-8%)','scale(1.22) translateY(0%)']   // bottom -> top
        : ['scale(1.22) translateY(0%)','scale(1.22) translateY(-8%)'];  // top -> bottom
    }
    // horizontal pan: top stays pinned, slide sideways
    return (t%2===0)
      ? ['scale(1.12) translateX(-3%)','scale(1.12) translateX(3%)']
      : ['scale(1.12) translateX(3%)','scale(1.12) translateX(-3%)'];
  }

  function cancelAnims(div){
    if(anims.has(div)){ anims.get(div).forEach(function(a){ try{a.cancel();}catch(e){} }); }
    anims.set(div, []);
  }

  // Per-image focal points for PORTRAIT only (x% y%). Picked so the vertical phone
  // crop lands on the interesting part of each wide image instead of dead center.
  var SPLASH_FOCUS = {1:'60.5% 57.4%',2:'50.1% 49.6%',3:'25.7% 49.5%',4:'36.3% 46.0%',5:'46.2% 47.1%',6:'49.7% 48.9%',7:'38.0% 58.3%',8:'20.4% 36.9%',9:'50.7% 42.5%',10:'54.7% 49.9%',11:'44.9% 37.8%',12:'51.2% 48.2%',13:'24.8% 48.5%',14:'53.8% 52.8%',15:'48.5% 48.5%',16:'55.7% 50.0%',17:'51.2% 33.7%',18:'55.5% 47.5%',19:'48.4% 49.4%',20:'54.8% 34.3%',21:'45.9% 43.9%'};
  // Zoom-into-point focal targets (x% y%) for DESKTOP + LANDSCAPE only.
  // In portrait these images fall back to a normal centered zoom.
  var ZOOM_INTO = {16:'55.6% 44.8%', 19:'48.2% 25.2%', 20:'55.6% 13.6%'};
  function isPortrait(){
    return window.innerWidth <= 1024 && window.matchMedia('(orientation:portrait)').matches;
  }
  function focusFor(n){
    // portrait: use the per-image focal point; otherwise center.
    if(isPortrait() && SPLASH_FOCUS[n]) return SPLASH_FOCUS[n];
    return '50% 50%';
  }
  // All splash images are now SHARP sources. Blur is done live in CSS and animated:
  // every slide emerges at 10px blur and resolves to 0px (fully sharp) across its full
  // time on screen — a slow continuous focus-pull, finishing as it crossfades out.
  function moveIn(div, n){
    cancelAnims(div);                       // clear any lingering forwards-fill
    if(REDUCE){                             // reduced motion: plain crossfade, no zoom/blur
      div.style.backgroundSize='cover';
      div.style.backgroundPosition=focusFor(n);
      anims.get(div).push(div.animate([{opacity:0},{opacity:1}],{duration:FADE,easing:'ease-in-out',fill:'forwards'}));
      return;
    }
    var m = motion[n] || 'zin';
    var tf = tfPair(n);
    div.style.backgroundSize='cover';

    // Zoom-into-point (16/19/20) on desktop+landscape: anchor the zoom AND the crop to
    // the focal point so the image zooms straight into that spot. Portrait ignores this.
    if(m==='zpt' && ZOOM_INTO[n] && !isPortrait()){
      div.style.backgroundPosition = ZOOM_INTO[n];
      div.style.transformOrigin    = ZOOM_INTO[n];
    } else if(m==='zctr'){
      // splash02: always zoom into the CENTER
      div.style.backgroundPosition = '50% 50%';
      div.style.transformOrigin    = 'center center';
    } else {
      div.style.backgroundPosition = focusFor(n);
      div.style.transformOrigin    = 'center top';   // default: top-anchored
    }

    var blurAnim = div.animate(
      [{filter:'blur(10px)'},{filter:'blur(0px)'}],
      {duration:MOTION_DUR, easing:'linear', fill:'forwards'}
    );
    anims.get(div).push(blurAnim);

    var mv = div.animate(
      [{transform:tf[0]}, {transform:tf[1]}],
      {duration:MOTION_DUR, easing:'linear', fill:'forwards'}
    );
    var fade = div.animate(
      [{opacity:0},{opacity:1}],
      {duration:FADE, easing:'ease-in-out', fill:'forwards'}
    );
    anims.get(div).push(mv, fade);
  }

  function fadeOut(div){
    var a = div.animate([{opacity:1},{opacity:0}],
      {duration:FADE, easing:'ease-in-out', fill:'forwards'});
    if(!anims.has(div)) anims.set(div,[]);
    anims.get(div).push(a);
  }

  function showFirst(src, n){
    front.style.backgroundImage='url("'+src+'")';
    moveIn(front, n);
  }
  function crossfade(src, n){
    var incoming=back, outgoing=front;
    incoming.style.backgroundImage='url("'+src+'")';
    moveIn(incoming, n);
    fadeOut(outgoing);
    front=incoming; back=outgoing;
  }

  function preload(src,cb,hi){ var im=new Image(); if(hi){ try{ im.fetchPriority='high'; }catch(e){} } im.onload=im.onerror=cb; im.src=src; }

  idx=Math.floor(Math.random()*imgs.length);
  var firstN=idx+1, firstSrc=imgs[idx]; idx=(idx+1)%imgs.length;
  preload(firstSrc, function(){ showFirst(firstSrc, firstN); }, true);

  setInterval(function(){
    var n=idx+1, src=imgs[idx]; idx=(idx+1)%imgs.length;
    preload(src, function(){ crossfade(src, n); });
  }, 10000);

  function probe(n){
    var im=new Image();
    im.onload=function(){ imgs.push(url(n)); if(!motion[n]) motion[n]=(n%2===0?'zout':'zin'); probe(n+1); };
    im.onerror=function(){};
    im.src=url(n);
  }
})();
(function(){
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav-row a[href^="#"]'));
  var sections = links.map(function(l){ return document.getElementById(l.getAttribute('href').slice(1)); });
  var dots = Array.prototype.slice.call(document.querySelectorAll('.rail a[href^="#"]'));
  var hold = 0, animating = null;

  function setActive(idx){
    links.forEach(function(l,i){ l.classList.toggle('active', i===idx); });
    dots.forEach(function(d,i){ d.classList.toggle('active', i===idx); });
  }
  function onScroll(){
    if (performance.now() < hold) return;
    var probe = window.scrollY + window.innerHeight*0.35;
    var idx = 0;
    for(var i=0;i<sections.length;i++){
      if(sections[i] && sections[i].offsetTop <= probe) idx = i;
    }
    // at the very bottom the last (short) section can never reach the probe line — mark it active
    if(window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) idx = sections.length - 1;
    setActive(idx);
  }

  // JS-driven ease that re-reads the target every frame and cannot stop short
  function glideTo(sec){
    if (animating) cancelAnimationFrame(animating);
    var start = window.scrollY;
    var t0 = performance.now();
    var D = 700; // ms
    function ease(t){ return t<.5 ? 2*t*t : 1-Math.pow(-2*t+2,2)/2; }
    function step(now){
      var t = Math.min(1,(now-t0)/D);
      var target = sec.offsetTop;            // live read - immune to shifts
      window.scrollTo(0, start + (target-start)*ease(t));
      if (t < 1) animating = requestAnimationFrame(step);
      else { window.scrollTo(0, sec.offsetTop); animating = null; }
    }
    animating = requestAnimationFrame(step);
  }
  ['wheel','touchstart'].forEach(function(ev){
    window.addEventListener(ev, function(){ if(animating){cancelAnimationFrame(animating);animating=null;} }, {passive:true});
  });

  links.forEach(function(l,i){
    l.addEventListener('click', function(e){
      var sec = sections[i];
      if(!sec) return;
      e.preventDefault();
      setActive(i);
      hold = performance.now() + 900;
      glideTo(sec);
      try{ history.replaceState(null,'','#'+sec.id); }catch(e){}
    });
  });

  dots.forEach(function(d,i){
    d.addEventListener('click', function(e){
      var sec = sections[i];
      if(!sec) return;
      e.preventDefault();
      setActive(i);
      hold = performance.now() + 900;
      glideTo(sec);
      try{ history.replaceState(null,'','#'+sec.id); }catch(e){}
    });
  });

  window.addEventListener('scroll', onScroll, {passive:true});
  window.addEventListener('resize', onScroll);
  onScroll();
})();
(function(){
  var lb    = document.getElementById('lb');
  var lbImg = document.getElementById('lb-img');
  var isPan = false;          // desktop vertical cursor-pan (Shut-in / inversion1)
  var isHPan = false;         // desktop horizontal cursor-pan
  var isClickPos = false;     // tl.jpg: start position set by click
  var startFrac = 0.5;        // where the click landed (0..1)
  var hpanActive = false;     // true after first mouse move post-open
  var hpanX = 0;              // current horizontal offset of the image (px)
  var hpanOverflow = 0;       // how far the image exceeds the viewport (px)
  var hpanLastClientX = null; // previous cursor X for delta calc
  var HPAN_GAIN = 2.6;        // movement amplification (wide image, small sweep)
  var tx=0, ty=0;             // current pan translation
  var dragging=false, moved=false, sx=0, sy=0, ox=0, oy=0;

  function isMobile(){ return window.innerWidth <= 1024; }

  function clampAndApply(){
    // keep the image from being dragged past its own edges
    var r = lbImg.getBoundingClientRect();
    var vw = window.innerWidth, vh = window.innerHeight;
    // overflow on each axis (how far the image exceeds the viewport)
    var imgW = lbImg.offsetWidth, imgH = lbImg.offsetHeight;
    var maxX = Math.max(0, (imgW - vw)/2);
    var maxY = Math.max(0, (imgH - vh)/2);
    if(tx >  maxX) tx =  maxX;
    if(tx < -maxX) tx = -maxX;
    if(ty >  maxY) ty =  maxY;
    if(ty < -maxY) ty = -maxY;
    lbImg.style.transform = 'translate('+tx+'px,'+ty+'px)';
  }

  function open(src, alt, pan, fitHeight, hpan, clickpos, fracX){
    lbImg.alt = alt||'';
    lbImg.src = '';
    lbImg.src = src;
    isPan  = !!pan  && !isMobile();        // vertical cursor-pan, desktop only
    isHPan = !!hpan && !isMobile();        // horizontal cursor-pan, desktop only
    isClickPos = !!clickpos;               // start position comes from the click fraction
    startFrac = (typeof fracX==='number') ? fracX : 0.5;
    hpanActive = false;                    // becomes true once the mouse moves (so the
                                           // click-set start isn't immediately overridden)
    lb.classList.toggle('pan-mode', isPan);
    lb.classList.toggle('hpan-mode', isHPan);
    lb.classList.toggle('fit-height', !!fitHeight || (!!hpan && isMobile()));
    tx=0; ty=0;
    document.body.style.overflow = 'hidden';

    if(isHPan){
      // Keep the image HIDDEN until it's positioned, so there is never a far-left frame
      // that then slides to the click position. No transition is involved; we just avoid
      // showing the default (translateX 0) state before place() runs.
      lbImg.style.visibility = 'hidden';
      lbImg.style.transform = '';
      lb.classList.add('open');
      var place = function(){
        var imgW = lbImg.offsetWidth, vw = window.innerWidth;
        hpanOverflow = imgW - vw;
        hpanX = (hpanOverflow <= 0) ? 0 : -(hpanOverflow * startFrac);
        lbImg.style.transform = 'translateX(' + hpanX + 'px)';
        lbImg.style.visibility = 'visible';   // reveal already in the right spot
      };
      if(lbImg.complete && lbImg.naturalWidth){ place(); }
      else { lbImg.onload = place; }
    } else {
      lbImg.style.visibility = '';
      lbImg.style.transform = '';
      lb.classList.add('open');
    }
  }
  function shut(){
    if(!lb.classList.contains('open')) return;
    lb.classList.remove('open','pan-mode','hpan-mode','fit-height','fitwidth-mode','dragging');
    lbImg.style.transform=''; lbImg.style.visibility=''; tx=0; ty=0;
    isPan=false; isHPan=false; isClickPos=false;
    hpanActive=false; hpanX=0; hpanOverflow=0; hpanLastClientX=null;
    lbImg.onload=null;
    document.body.style.overflow='';
    if(ui) ui.hidden=true;
    clearHash();
  }

  // ---- gallery model: every linked artwork inside a .shots block, in page order ----
  var IMG_RE=/\.(jpg|jpeg|png|webp)(\?|$)/i;
  var cur=-1, list=[];
  function gallery(){ list=Array.prototype.slice.call(document.querySelectorAll('.shots a[href]')).filter(function(a){ return IMG_RE.test(a.getAttribute('href')||''); }); return list; }
  function pathOf(a){ return (a.getAttribute('href')||'').replace(/^https?:\/\/[^\/]+/,'').replace(/^\//,''); }

  var ui=document.getElementById('lb-ui'), cap=document.getElementById('lb-cap'), cnt=document.getElementById('lb-count');
  function updateUI(a){
    if(!ui) return;
    var art=a.closest('article'); var h=art&&art.querySelector('h3');
    var img=a.querySelector('img.a')||a.querySelector('img');
    var t=h?h.textContent:'', al=(img&&img.alt)||'';
    cap.textContent = !al ? t : (al.toLowerCase().indexOf(t.toLowerCase().slice(0,12))===0 ? al : t+' — '+al);
    cnt.textContent=(cur+1)+' / '+list.length;
    ui.hidden=false;
  }
  function setHash(a){ try{ history.replaceState(null,'','#view='+encodeURI(pathOf(a))); }catch(e){} }
  function clearHash(){
    if(location.hash.indexOf('#view=')!==0) return;
    var a=list[cur], sec=a&&a.closest('section');
    try{ history.replaceState(null,'', sec?'#'+sec.id : location.pathname+location.search); }catch(e){}
  }

  function openAnchor(a, e){
    var img = a.querySelector('img.a') || a.querySelector('img:not(.b)') || a.querySelector('img');
    var pan = a.getAttribute('data-pan') === 'true';
    var fitH = a.getAttribute('data-fit') === 'height';
    var hpan = a.getAttribute('data-hpan') === 'true';
    var clickpos = a.getAttribute('data-clickpos') === 'true';
    var fitWidth = a.getAttribute('data-fitwidth') === 'true';
    // for click-position images: where (0..1) across the thumbnail did the user click?
    var fracX = 0.5;
    if(clickpos && img && e){
      var r = img.getBoundingClientRect();
      fracX = (e.clientX - r.left) / r.width;
      if(fracX < 0) fracX = 0;
      if(fracX > 1) fracX = 1;
    }
    gallery(); cur=list.indexOf(a);
    lb.classList.toggle('fitwidth-mode', fitWidth);
    open(a.getAttribute('href'), img ? img.alt : '', pan, fitH, hpan, clickpos, fracX);
    updateUI(a); setHash(a);
  }
  function step(d){
    if(!lb.classList.contains('open')) return;
    gallery(); if(!list.length) return;
    var n=(cur+d+list.length)%list.length, a=list[n];
    lb.classList.remove('pan-mode','hpan-mode','fit-height','fitwidth-mode');
    openAnchor(a,null);
  }

  // open from gallery clicks
  document.addEventListener('click', function(e){
    var a = e.target.closest('a[href]');
    if(!a || a.closest('#lb')) return;
    var href = a.getAttribute('href')||'';
    if(!IMG_RE.test(href)) return;
    e.preventDefault();
    if(a.getAttribute('data-dragged')==='1'){ a.removeAttribute('data-dragged'); return; } // compare-slider drag, not a click
    openAnchor(a, e);
  });

  // lightbox chrome: prev / next / close / copy-link
  function btn(id,fn){ var b=document.getElementById(id); if(b) b.addEventListener('click',function(e){ e.stopPropagation(); fn(); }); }
  btn('lb-prev',function(){ step(-1); });
  btn('lb-next',function(){ step(1); });
  btn('lb-close',function(){ shut(); });
  btn('lb-link',function(){
    var b=document.getElementById('lb-link');
    var url=location.href;
    var done=function(){ b.textContent='Link copied'; setTimeout(function(){ b.textContent='Copy link'; },1600); };
    if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(url).then(done,function(){}); }
  });
  if(ui){ ui.addEventListener('click',function(e){ e.stopPropagation(); }); }

  // swipe left/right to change image (only when the image is not wider than the screen,
  // otherwise horizontal drags keep panning the image as before)
  var swX=null, swY=null, swOK=false;
  lb.addEventListener('touchstart',function(e){
    if(e.touches.length!==1){ swX=null; return; }
    swX=e.touches[0].clientX; swY=e.touches[0].clientY;
    swOK = lbImg.offsetWidth <= window.innerWidth + 2;
  },{passive:true});
  lb.addEventListener('touchend',function(e){
    if(swX===null||!swOK) return;
    var t=e.changedTouches[0], dx=t.clientX-swX, dy=t.clientY-swY; swX=null;
    if(Math.abs(dx)>50 && Math.abs(dx)>Math.abs(dy)*1.5){ moved=true; step(dx<0?1:-1); }
  },{passive:true});

  // deep links: patlau.com/#view=matte/dc.jpg opens that artwork directly
  function fromHash(){
    if(location.hash.indexOf('#view=')!==0) return;
    var p=decodeURI(location.hash.slice(6));
    var a=gallery().filter(function(x){ return pathOf(x)===p; })[0];
    if(a){ var sec=a.closest('section'); if(sec) window.scrollTo(0, sec.offsetTop); openAnchor(a,null); }
  }
  window.addEventListener('hashchange', fromHash);
  if(document.readyState==='complete') fromHash(); else window.addEventListener('load', fromHash);

  // ---- DRAG TO PAN (mouse + touch) ----
  function start(x,y){
    dragging=true; moved=false; sx=x; sy=y; ox=tx; oy=ty;
    lb.classList.add('dragging');
  }
  function move(x,y){
    if(!dragging) return;
    var dx=x-sx, dy=y-sy;
    if(Math.abs(dx)>3||Math.abs(dy)>3) moved=true;
    tx=ox+dx; ty=oy+dy;
    clampAndApply();
  }
  function end(){ dragging=false; lb.classList.remove('dragging'); }

  // mouse
  lbImg.addEventListener('mousedown', function(e){ if(isPan||isHPan) return; e.preventDefault(); start(e.clientX,e.clientY); });
  window.addEventListener('mousemove', function(e){ if(dragging){ move(e.clientX,e.clientY); } });
  window.addEventListener('mouseup', function(){ end(); });

  // touch
  lbImg.addEventListener('touchstart', function(e){
    if(e.touches.length===1){ start(e.touches[0].clientX, e.touches[0].clientY); }
  }, {passive:true});
  lbImg.addEventListener('touchmove', function(e){
    if(dragging && e.touches.length===1){ move(e.touches[0].clientX, e.touches[0].clientY); }
  }, {passive:true});
  lbImg.addEventListener('touchend', function(){ end(); }, {passive:true});

  // closing rules:
  //  - cursor-pan modes (isPan/isHPan): a click anywhere, incl. the image, closes
  //  - drag-pan images: image click closes only if it wasn't a drag
  //  - background click always closes
  lb.addEventListener('click', function(e){
    if(isPan || isHPan){ shut(); return; }      // cursor-pan: click image OR bg exits
    if(e.target!==lbImg){ shut(); return; }     // background always closes
    if(moved) return;                           // ignore click that ended a drag
    shut();                                     // plain click on image closes
  });

  document.addEventListener('keydown', function(e){
    if(!lb.classList.contains('open')) return;
    if(e.key==='Escape') shut();
    else if(e.key==='ArrowRight'){ e.preventDefault(); step(1); }
    else if(e.key==='ArrowLeft'){ e.preventDefault(); step(-1); }
  });

  // desktop vertical cursor pan (Shut-in / inversion1): fit width, move up/down
  lb.addEventListener('mousemove', function(e){
    if(!isPan) return;
    var imgH = lbImg.naturalHeight * (window.innerWidth / lbImg.naturalWidth);
    var overflow = imgH - window.innerHeight;
    if(overflow <= 0){ lbImg.style.transform=''; return; }
    var rel = e.clientY / window.innerHeight;
    lbImg.style.transform = 'translateY(' + (-(overflow*rel)) + 'px)';
  });

  // desktop horizontal pan (The Creator / tl.jpg): fit height.
  // BLEND mixes two pan models each frame:
  //   relativeTarget = current pos + (mouse delta * gain)   [feels like the 100% version]
  //   absoluteTarget = cursor screen-X fraction * overflow  [sweep whole screen = whole image]
  // result = BLEND*relative + (1-BLEND)*absolute.  Lower BLEND => less sensitive / more 1:1.
  var HPAN_BLEND = 0.0;   // 0% relative, 100% absolute (pure cursor-position mapping)
  lb.addEventListener('mousemove', function(e){
    if(!isHPan){ hpanLastClientX = null; return; }
    if(hpanOverflow <= 0){ return; }
    if(hpanLastClientX === null){ hpanLastClientX = e.clientX; }
    var dx = e.clientX - hpanLastClientX;
    hpanLastClientX = e.clientX;

    // relative target: accumulate delta from current position
    var relTarget = hpanX - dx * HPAN_GAIN;

    // absolute target: cursor position across the screen maps to image position
    var rel = e.clientX / window.innerWidth;   // 0 at left edge, 1 at right edge
    if(rel < 0) rel = 0; if(rel > 1) rel = 1;
    var absTarget = -(hpanOverflow * rel);

    // blend
    hpanX = HPAN_BLEND * relTarget + (1 - HPAN_BLEND) * absTarget;

    // clamp to image edges
    if(hpanX > 0) hpanX = 0;
    if(hpanX < -hpanOverflow) hpanX = -hpanOverflow;
    lbImg.style.transform = 'translateX(' + hpanX + 'px)';
  });
})();
(function(){
  var banner=document.querySelector('.banner');
  var lastY=window.scrollY, ticking=false, hidden=false;
  var upAccum=0;                 // cumulative upward scroll while hidden
  var HIDE_AT=5, REVEAL_AT=60;   // hide after 5px down; reveal after 60px up
  window.addEventListener('scroll',function(){
    if(ticking)return;
    ticking=true;
    requestAnimationFrame(function(){
      if(window.innerWidth>1024){
        banner.style.transform='';
        hidden=false; upAccum=0;
        lastY=window.scrollY; ticking=false; return;
      }
      var y=window.scrollY;
      var dy=y-lastY;
      if(dy>0){
        // scrolling down
        upAccum=0;
        if(!hidden && y>HIDE_AT){
          banner.style.transform='translateY(-100%)';
          hidden=true;
        }
      } else if(dy<0){
        // scrolling up — accumulate; only reveal after REVEAL_AT
        upAccum += -dy;
        if(hidden && upAccum>=REVEAL_AT){
          banner.style.transform='translateY(0)';
          hidden=false; upAccum=0;
        }
      }
      // always show at very top
      if(y<=HIDE_AT){ banner.style.transform='translateY(0)'; hidden=false; upAccum=0; }
      lastY=y; ticking=false;
    });
  },{passive:true});
})();
(function(){
  var player=document.getElementById('player');
  var audio=document.getElementById('audio');
  var canvas=document.getElementById('wave');
  var ctx=canvas.getContext('2d');
  var muted=true, raf, started=false;


  // White 1px columns packed edge-to-edge across the red square — a chaotic
  // pixel waveform. Each column has its own random rhythm so it looks turbulent.
  var t0=Date.now();
  var COLS=canvas.width;          // one column per pixel of width (64) => >=25
  var P=[];
  for(var k=0;k<COLS;k++){
    P.push({
      f1: 3.0 + Math.random()*5.0,
      f2: 9.0 + Math.random()*8.0,
      f3: 18.0 + Math.random()*15.0,
      ph1: Math.random()*6.28,
      ph2: Math.random()*6.28,
      ph3: Math.random()*6.28
    });
  }
  function draw(){
    raf = requestAnimationFrame(draw);
    var w = canvas.width, h = canvas.height;
    ctx.clearRect(0, 0, w, h);
    var tt = (Date.now() - t0) / 1000;
    var playing = audio && !audio.paused && !audio.muted;
    var amp = playing ? 0.95 : 0.55;   // taller bounce when actually playing
    var spd = muted ? 1.0 : 2.0;
    var DOT = 2;                        // 2x2 px dots (was 1x1)
    ctx.fillStyle = '#ffffff';
    for(var x=0; x<w; x+=DOT){          // step by dot size so 2px dots don't overlap
      var p = P[x];
      var v = Math.sin(tt*p.f1*spd + p.ph1)*0.5
            + Math.sin(tt*p.f2*spd + p.ph2)*0.32
            + Math.sin(tt*p.f3*spd + p.ph3)*0.18;
      var cy = h/2 - v*amp*(h/2);       // amp up to ~0.95 of half-height => reaches top
      if(cy < 0) cy = 0;
      if(cy > h-DOT) cy = h-DOT;
      ctx.fillRect(x, cy, DOT, DOT);
    }
  }

  function startPlayback(){
    audio.loop=true;
    audio.volume=1;
    audio.muted=false;
    audio.play().catch(function(e){ console.log('play failed',e); });
    muted=false;
  }
  function stopPlayback(){
    audio.pause();
    muted=true;
  }
  // Toggle reads the ACTUAL audio state (audio.paused), not a separate variable that
  // can desync after an orientation change. Uses real play/pause, not muting.
  function toggle(e){
    if(e) e.stopPropagation();
    if(audio.paused){
      startPlayback();
    } else {
      stopPlayback();
    }
    // keep the waveform's muted flag in sync with reality
    muted = audio.paused;
  }

  player.addEventListener('click', toggle);   // native <button>: Enter/Space already fire click
  function syncPressed(){ var on=!audio.paused; player.setAttribute('aria-pressed', on?'true':'false'); player.setAttribute('aria-label', on?'Pause background music':'Play background music'); }
  audio.addEventListener('play', syncPressed); audio.addEventListener('pause', syncPressed);

  draw();                 // waveform runs forever (visual only, no audio)
  // Audio does NOT auto-start. It plays ONLY when the user clicks the waveform.
  // Ensure it begins paused/muted so nothing leaks until the user toggles it.
  audio.pause();
  muted = true;
})();
/* ---- CONTACT: e-mail / phone are assembled at runtime so they never sit in the page source ---- */
(function(){
  var EMAIL=['patlau','com'].join('.')+'@'+['gmail','com'].join('.');
  var PHONE=['+1','647','921','8241'];
  var PHONE_TEL=PHONE.join(''), PHONE_TXT=PHONE[0]+' '+PHONE[1]+' '+PHONE[2]+' '+PHONE[3];
  var GMAIL='https://mail.google.com/mail/?view=cm&fs=1&to='+encodeURIComponent(EMAIL);
  var coarse=window.matchMedia&&window.matchMedia('(pointer:coarse)').matches;
  var pop=null, owner=null;

  function copy(text, el){
    var done=function(){ var t=el.textContent; el.textContent='Copied ✓'; setTimeout(function(){ el.textContent=t; },1500); };
    if(navigator.clipboard&&navigator.clipboard.writeText){ navigator.clipboard.writeText(text).then(done,function(){ fallback(); }); }
    else fallback();
    function fallback(){ var ta=document.createElement('textarea'); ta.value=text; ta.setAttribute('readonly',''); ta.style.position='fixed'; ta.style.opacity='0'; document.body.appendChild(ta); ta.select(); try{ document.execCommand('copy'); done(); }catch(e){} ta.remove(); }
  }
  function close(){ if(pop){ pop.remove(); pop=null; if(owner) owner.setAttribute('aria-expanded','false'); owner=null; } }
  function item(label, href, fn, ext){
    var a=document.createElement(href?'a':'button');
    a.className='cpop-item'; a.textContent=label;
    if(href){ a.href=href; if(ext){ a.target='_blank'; a.rel='noopener noreferrer'; } a.addEventListener('click', close); }
    else { a.type='button'; a.addEventListener('click', function(e){ e.stopPropagation(); fn(a); }); }
    return a;
  }
  function openPop(btn, kind){
    if(owner===btn){ close(); return; }
    close();
    pop=document.createElement('div'); pop.className='cpop'; pop.setAttribute('role','menu');
    var v=document.createElement('p'); v.className='cpop-val'; v.textContent= kind==='email'?EMAIL:PHONE_TXT; pop.appendChild(v);
    if(kind==='email'){
      pop.appendChild(item('Write in Gmail', GMAIL, null, true));
      pop.appendChild(item('Open mail app', 'mailto:'+EMAIL));
      pop.appendChild(item('Copy address', null, function(el){ copy(EMAIL, el); }));
    } else {
      pop.appendChild(item('Call', 'tel:'+PHONE_TEL));
      pop.appendChild(item('Copy number', null, function(el){ copy(PHONE_TXT, el); }));
    }
    document.body.appendChild(pop);
    var r=btn.getBoundingClientRect(), pw=pop.offsetWidth;
    var left=Math.min(Math.max(8, r.left + r.width/2 - pw/2), window.innerWidth - pw - 8);
    pop.style.left=left+'px'; pop.style.top=(r.bottom+8)+'px';
    owner=btn; btn.setAttribute('aria-expanded','true');
    var first=pop.querySelector('.cpop-item'); if(first) first.focus({preventScroll:true});
  }
  document.querySelectorAll('[data-contact]').forEach(function(b){
    var kind=b.getAttribute('data-contact');
    b.setAttribute('aria-haspopup','menu'); b.setAttribute('aria-expanded','false');
    if(kind==='tel') b.setAttribute('href','tel:'+PHONE_TEL);
    if(kind==='email') b.setAttribute('href','mailto:'+EMAIL);
    b.addEventListener('click', function(e){
      if(kind==='tel' && coarse) return;            // phones: tap-to-call straight away, as before
      e.preventDefault(); e.stopPropagation(); openPop(b, kind);
    });
  });
  document.addEventListener('click', function(e){ if(pop && !pop.contains(e.target)) close(); });
  document.addEventListener('keydown', function(e){ if(e.key==='Escape') close(); });
  window.addEventListener('scroll', close, {passive:true});
  window.addEventListener('resize', close);
})();

/* ---- BEFORE / AFTER: plate vs final wipe on the .roll pairs (hover on desktop, drag on touch) ---- */
(function(){
  var rolls=document.querySelectorAll('a.roll');
  rolls.forEach(function(a){
    var inner=a.querySelector('.inner'); if(!inner||!a.querySelector('img.b')) return;
    a.classList.add('cmp');
    var bar=document.createElement('span'); bar.className='cmp-bar'; bar.setAttribute('aria-hidden','true');
    var l1=document.createElement('span'); l1.className='cmp-lbl cmp-l'; l1.textContent='Plate'; l1.setAttribute('aria-hidden','true');
    var l2=document.createElement('span'); l2.className='cmp-lbl cmp-r'; l2.textContent='Final'; l2.setAttribute('aria-hidden','true');
    inner.appendChild(bar); inner.appendChild(l1); inner.appendChild(l2);
    var pos=0, drag=false, startX=0, startY=0, dragged=false;
    function set(p,settle){ pos=Math.max(0,Math.min(100,p)); a.classList.toggle('settle',!!settle); a.style.setProperty('--pos',pos+'%'); a.classList.toggle('cmp-on',pos>0.5); }
    function fromEvent(e){ var r=inner.getBoundingClientRect(); return (e.clientX-r.left)/r.width*100; }
    a.addEventListener('pointermove',function(e){
      if(e.pointerType==='mouse'){ set(fromEvent(e)); return; }
      if(!drag) return;
      if(!dragged && Math.abs(e.clientX-startX)>6 && Math.abs(e.clientX-startX)>Math.abs(e.clientY-startY)) dragged=true;
      if(dragged){ set(fromEvent(e)); }
    });
    a.addEventListener('pointerleave',function(e){ if(e.pointerType==='mouse') set(0,true); });
    a.addEventListener('pointerdown',function(e){ if(e.pointerType!=='mouse'){ drag=true; dragged=false; startX=e.clientX; startY=e.clientY; } });
    a.addEventListener('pointerup',function(){ if(drag && dragged) a.setAttribute('data-dragged','1'); drag=false; });
    a.addEventListener('pointercancel',function(){ drag=false; });
    a.addEventListener('keydown',function(e){
      if(e.key==='ArrowRight'){ e.preventDefault(); set(pos+10,true); }
      else if(e.key==='ArrowLeft'){ e.preventDefault(); set(pos-10,true); }
    });
    a.addEventListener('blur',function(){ set(0,true); });
  });
})();

/* ---- VIMEO: lightweight click-to-play posters; the Vimeo player loads only when asked ---- */
(function(){
  document.querySelectorAll('.vfac').forEach(function(box){
    var b=box.querySelector('.vplay'); if(!b) return;
    b.addEventListener('click',function(){
      var id=box.getAttribute('data-vimeo'), extra=box.getAttribute('data-params')||'';
      var f=document.createElement('iframe');
      f.src='https://player.vimeo.com/video/'+id+'?autoplay=1&dnt=1'+(extra?'&'+extra:'');
      f.title=b.getAttribute('data-title')||'Video';
      f.allow='autoplay; fullscreen; picture-in-picture';
      f.setAttribute('allowfullscreen','');
      box.innerHTML=''; box.appendChild(f); box.classList.add('live');
    });
  });
})();

/* ---- LOOPING BREAKDOWNS (former GIFs): load + play only when on screen; respect reduced motion ---- */
(function(){
  var vids=document.querySelectorAll('video.loopvid'); if(!vids.length) return;
  var reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  function load(v){
    if(v.dataset.loaded) return;
    var fb=v.firstChild;   // keep the GIF <img> fallback last
    [['webm','video/webm'],['mp4','video/mp4']].forEach(function(t){
      var u=v.getAttribute('data-'+t[0]); if(!u) return;
      var s=document.createElement('source'); s.src=u; s.type=t[1]; v.insertBefore(s, fb);
    });
    v.load(); v.dataset.loaded='1';
  }
  if(reduce){ vids.forEach(function(v){ v.removeAttribute('autoplay'); v.loop=true; v.preload='none'; v.controls=true; load(v); }); return; }
  if(!('IntersectionObserver' in window)){ vids.forEach(function(v){ load(v); v.play().catch(function(){}); }); return; }
  var io=new IntersectionObserver(function(es){
    es.forEach(function(en){ var v=en.target;
      if(en.isIntersecting){ load(v); var p=v.play(); if(p&&p.catch) p.catch(function(){}); }
      else if(v.dataset.loaded){ v.pause(); }
    });
  },{rootMargin:'300px 0px'});
  vids.forEach(function(v){ io.observe(v); });
})();
