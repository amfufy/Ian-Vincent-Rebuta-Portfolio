/* Content is plain HTML above, so search engines and AI crawlers can read it without JavaScript.
   This script only adds the filter control, reveal motion and one-video-at-a-time playback. */
const $=s=>document.querySelector(s);
const cases=[...document.querySelectorAll(".case")];
function moveThumb(){
  const b=$('#filters button[aria-pressed="true"]'), t=$("#filters .thumb");
  if(!b||!t) return;
  t.style.width=b.offsetWidth+"px";
  t.style.transform=`translateX(${b.offsetLeft}px)`;
}
function applyFilter(cat, animate){
  let n=0;
  cases.forEach(el=>{
    const show = cat==="all" || el.dataset.cats.split(" ").includes(cat);
    el.hidden=!show;
    el.classList.toggle("flip", show && (n++ % 2 === 1));
    el.classList.remove("pop");
    if(show){
      el.querySelectorAll(".rv").forEach(r=>r.classList.add("in"));
      if(animate){ void el.offsetWidth; el.style.animationDelay=Math.min(n-1,4)*60+"ms"; el.classList.add("pop"); }
    }
  });
  document.querySelectorAll("#filters button").forEach(b=>b.setAttribute("aria-pressed", b.dataset.cat===cat));
  moveThumb();
  const f=$("#filters"), b=$('#filters button[aria-pressed="true"]');
  if(animate && b && f.scrollWidth>f.clientWidth) f.scrollTo({left:b.offsetLeft-(f.clientWidth-b.offsetWidth)/2, behavior:"smooth"});
}
$("#filters").addEventListener("click", e=>{
  const b=e.target.closest("button");
  if(!b || b.getAttribute("aria-pressed")==="true") return;
  applyFilter(b.dataset.cat, true);
  if (window.gtag) gtag("event","filter_work",{category:b.dataset.cat});
});
applyFilter("all");
cases.forEach(el=>el.querySelectorAll(".rv").forEach(r=>r.classList.remove("in")));
addEventListener("resize", moveThumb);
document.fonts && document.fonts.ready.then(moveThumb);

// only one video plays at a time
document.addEventListener("play", e=>{ document.querySelectorAll("video").forEach(v=>{ if(v!==e.target) v.pause(); }); }, true);

// spring reveal on scroll
const io=new IntersectionObserver(es=>es.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add("in"); io.unobserve(e.target); } }),{threshold:.12});
document.querySelectorAll(".rv").forEach(el=>io.observe(el));

// sticky "Book a call" bar appears after the hero, hides at the contact section
const bar=$("#ctabar");
if(bar){
  const hero=$("#overview"), contact=$("#contact"); let pastHero=false, atContact=false;
  const set=()=>bar.classList.toggle("show", pastHero && !atContact);
  new IntersectionObserver(([e])=>{ pastHero=!e.isIntersecting; set(); }).observe(hero);
  new IntersectionObserver(([e])=>{ atContact=e.isIntersecting; set(); }).observe(contact);
}

// today's date in the dashboard header
const today=$("#today"); if(today) today.textContent=new Date().toLocaleDateString("en-US",{weekday:"long",month:"long",day:"numeric"});

// world clock widget: Bohol and New York, with a live "online" status during US business hours
function tzParts(tz){ const f=new Intl.DateTimeFormat("en-US",{timeZone:tz,hour:"numeric",minute:"2-digit",second:"2-digit",hour12:false,weekday:"short"}).formatToParts(new Date()); const g=t=>f.find(p=>p.type===t).value; return {h:+g("hour")%24,m:+g("minute"),s:+g("second"),wd:g("weekday")}; }
function tick(){
  [["cb","Asia/Manila"],["cn","America/New_York"]].forEach(([id,tz])=>{
    const t=tzParts(tz), hh=document.getElementById(id+"h"); if(!hh) return;
    hh.style.transform=`rotate(${(t.h%12)*30+t.m/2}deg)`;
    document.getElementById(id+"m").style.transform=`rotate(${t.m*6+t.s/10}deg)`;
    document.getElementById(id+"s").style.transform=`rotate(${t.s*6}deg)`;
    document.getElementById(id+"t").textContent=new Date().toLocaleTimeString("en-US",{timeZone:tz,hour:"numeric",minute:"2-digit"});
  });
  const ny=tzParts("America/New_York"), st=$("#status");
  if(st){ const open=!["Sat","Sun"].includes(ny.wd) && ny.h>=8 && ny.h<18; st.classList.toggle("live",open); st.textContent=open?"Online now":"Back in US business hours"; }
}
tick(); setInterval(tick,1000);

// highlight the current section in the sidebar and tab bar
const spyLinks=[...document.querySelectorAll("[data-spy]")];
const spy=new IntersectionObserver(es=>es.forEach(e=>{ if(e.isIntersecting){ spyLinks.forEach(a=>a.classList.toggle("on",a.dataset.spy===e.target.id)); } }),{rootMargin:"-45% 0px -50% 0px"});
["overview","support","work","experience","process","faq","contact"].forEach(id=>{ const el=document.getElementById(id); if(el) spy.observe(el); });
