/* Service worker : réseau d'abord (les mises à jour arrivent tout de suite), copie locale si pas de réseau */
const CACHE="map-v9";
const CORE=["./","./index.html","./manifest.webmanifest","./icons/icon-192.png","./icons/icon-512.png","./icons/apple-touch-icon.png","./vendor/html2canvas.min.js","./vendor/jspdf.umd.min.js","./fonts/ibm-plex-sans-latin-400-normal.woff2","./fonts/ibm-plex-sans-latin-500-normal.woff2","./fonts/ibm-plex-sans-latin-600-normal.woff2","./fonts/ibm-plex-mono-latin-400-normal.woff2","./fonts/ibm-plex-mono-latin-500-normal.woff2","./fonts/ibm-plex-mono-latin-600-normal.woff2","./fonts/newsreader-latin-500-normal.woff2","./fonts/newsreader-latin-600-normal.woff2"];
self.addEventListener("install",e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting()));});
self.addEventListener("activate",e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener("fetch",e=>{
  const r=e.request;if(r.method!=="GET")return;
  const u=new URL(r.url);
  const same=u.origin===location.origin, fonts=/fonts\.(googleapis|gstatic)\.com$/.test(u.hostname);
  if(!same&&!fonts)return;
  e.respondWith(fetch(r).then(res=>{if(res&&(res.ok||res.type==="opaque")){const cp=res.clone();caches.open(CACHE).then(c=>c.put(r,cp));}return res;})
    .catch(()=>caches.match(r,{ignoreSearch:true}).then(m=>m||(r.mode==="navigate"?caches.match("./index.html"):undefined))));
});
