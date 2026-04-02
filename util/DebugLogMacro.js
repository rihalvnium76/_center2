// https://www.toptal.com/developers/javascript-minifier

/** @deprecated */
function LiteLogFactoryV3(tag, parent = {}, id = String(Math.random()).slice(2)) {
  function Log(...v) {
    console.log(tag, id, ...v);
  }
  Log.tag = tag;
  Log.id = id;
  Log.t = (...v) => Log('<-', parent.tag, parent.id, ...v);
  return Log;
}
/** @deprecated */
function LiteLogFactoryV3(b,d={},c=String(Math.random()).slice(2)){function a(...a){console.log(b,c,...a)}return a.tag=b,a.id=c,a.t=(...b)=>a("<-",d.tag,d.id,...b),a}

// v4.4
function LogFactoryV4(tag, parent, id = String(Math.random()).slice(2), head = n => `[${tag} ${id}]${n && parent ? parent.h(--n) : ""}`, generator = n => (...v) => console.log(head(n), ...v), Log = generator(0)) {
  Log.h = head
  /** Log with parent*/
  Log.t = generator(1)
  /** Log with stack */
  Log.s = generator(-1)
  return Log
}

function LogFactoryV4(o,n,r=String(Math.random()).slice(2),t=t=>`[${o} ${r}]${t&&n?n.h(--t):""}`,c=o=>(...n)=>console.log(t(o),...n),a=c(0)){return a.h=t,a.t=c(1),a.s=c(-1),a}

/// with comments
function LogFactoryV4(/** string tag */ o, /** parent Log */ n,/** @immutable id */ r=String(Math.random()).slice(2), /** @immutable log head (tag + id) */ t=t=>`[${o} ${r}]${t&&n?n.h(--t):""}`, /** @immutable log function generator */ c=o=>(...n)=>console.log(t(o),...n), /** @immutable Logger (usage: log(...)) */ a=c(0)){return a.h=t, /** log with parent head (usage: log.t(...)) */ a.t=c(1), /** log with stack (usage: log.s(...)) */ a.s=c(-1),a}

// function LogFactoryV4(o:string,n:any,r=String(Math.random()).slice(2),t=(t:any)=>`[${o} ${r}]${t&&n?n.h(--t):""}`,c=(o:any)=>(...n:any)=>console.log(t(o),...n),a:any=c(0)){return a.h=t,a.t=c(1),a.s=c(-1),a}

let a=LogFactoryV4('A'),b=LogFactoryV4('B',a),c=LogFactoryV4('C',b)
c(1)
c.t(2)
c.s(4)
