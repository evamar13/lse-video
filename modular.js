'use strict';
// Motor técnico 2D compartido. No interpreta texto ni determina profundidad.
const MODULAR=(()=>{
const add=(a,b)=>[a[0]+b[0],a[1]+b[1]], sub=(a,b)=>[a[0]-b[0],a[1]-b[1]], mul=(a,s)=>[a[0]*s,a[1]*s];
const norm=a=>Math.hypot(...a), distance=(a,b)=>norm(sub(a,b));
function ik(shoulder,target,upper,lower,bend){
 const delta=sub(target,shoulder),requested=norm(delta);
 const d=Math.max(Math.abs(upper-lower)+.001,Math.min(upper+lower-.001,requested));
 const direction=requested>.0001?mul(delta,1/requested):[0,1];
 const wrist=add(shoulder,mul(direction,d));
 const along=(upper*upper-lower*lower+d*d)/(2*d),offset=Math.sqrt(Math.max(0,upper*upper-along*along));
 const elbow=add(add(shoulder,mul(direction,along)),mul([-direction[1],direction[0]],bend*offset));
 return {elbow,wrist,error:distance(wrist,target),reachable:Math.abs(d-requested)<.01};
}
const fingers=[[0,1,2,3,4],[0,5,6,7,8],[0,9,10,11,12],[0,13,14,15,16],[0,17,18,19,20]];
const faceOval=[10,338,297,332,284,251,389,356,454,323,361,288,397,365,379,378,400,377,152,148,176,149,150,136,172,58,132,93,234,127,162,21,54,103,67,109];
const features=[[61,40,37,0,267,270,291,321,314,17,84,91,61],[78,81,13,311,308,402,14,87,78],[33,160,158,133,153,144,33],[362,385,387,263,373,380,362],[70,63,105,66,107],[336,296,334,293,300]];
const profiles=[{name:'A · hombros y brazos de referencia',skin:'#d8a47e',shade:'#b77a59',shirt:'#527c75',hair:'#5b3931',width:1,arm:1},
 {name:'B · hombros más anchos y brazos más largos',skin:'#8d5945',shade:'#6d3e32',shirt:'#b16a79',hair:'#242c33',width:1.22,arm:1.15}];
function setup(first){
 const p=first.pose,c=mul(add(p['11'],p['12']),.5),unit=distance(p['11'],p['12']);
 if(unit<=.01)throw Error('Referencia de hombros no válida');
 const canonical=q=>mul(sub(q,c),1/unit);
 const arms={};for(const [name,a,b,d] of [['left',11,13,15],['right',12,14,16]])arms[name]=[distance(p[a],p[b])/unit,distance(p[b],p[d])/unit];
 return {canonical,arms};
}
function pose(frame,profile,model,mode){
 const transform=q=>add([250,265],mul(model.canonical(q),158));
 const face={};for(const [key,value] of Object.entries(frame.face))face[key]=transform(value);
 const shoulders={left:add([250,265],mul(sub(transform(frame.pose['11']),[250,265]),profile.width)),right:add([250,265],mul(sub(transform(frame.pose['12']),[250,265]),profile.width))};
 const hands={},arms={},warnings=[];
 for(const [name,key,side] of [['left','left_hand',-1],['right','right_hand',1]]){
  const source=frame[key];if(!source.length){hands[name]=[];warnings.push('Mano '+name+' ausente');continue;}
  let points=source.map(transform),target=points[0];
  if(mode==='contact'&&name==='left'&&face['234']){
   // Diagnóstico técnico: colocar la punta del índice sobre una marca de mejilla.
   const shift=sub(face['234'],points[8]);points=points.map(p=>add(p,shift));target=points[0];
  }
  const lengths=model.arms[name].map(v=>v*158*profile.arm);
  const solution=ik(shoulders[name],target,...lengths,side);
  if(!solution.reachable){warnings.push('Objetivo fuera de alcance ('+name+')');}
  const displacement=sub(solution.wrist,target);
  hands[name]=points.map(p=>add(p,displacement));arms[name]={...solution,shoulder:shoulders[name]};
 }
 const hipLeft=transform(frame.pose['23']),hipRight=transform(frame.pose['24']);
 return {face,shoulders,hands,arms,warnings,hips:[hipLeft,hipRight],contact:mode==='contact'?face['234']:null};
}
function path(ctx,points,close=false){if(!points.length)return;ctx.beginPath();ctx.moveTo(...points[0]);for(const p of points.slice(1))ctx.lineTo(...p);if(close)ctx.closePath();}
function draw(canvas,frame,profile,model,options={}){
 const start=performance.now(),ctx=canvas.getContext('2d'),p=pose(frame,profile,model,options.mode||'observation');
 ctx.clearRect(0,0,500,570);ctx.fillStyle='#f3eee4';ctx.fillRect(0,0,500,570);
 const left=p.shoulders.left,right=p.shoulders.right,hips=p.hips;
 ctx.fillStyle=profile.shirt;path(ctx,[add(left,[-14,-8]),add(right,[14,-8]),add(hips[1],[12,20]),add(hips[0],[-12,20])],true);ctx.fill();
 ctx.strokeStyle='#ffffff44';ctx.lineWidth=2;path(ctx,[[250,278],[250,hips[0][1]+15]]);ctx.stroke();
 for(const a of Object.values(p.arms)){
  ctx.lineCap='round';ctx.lineJoin='round';ctx.strokeStyle=profile.shade;ctx.lineWidth=27;path(ctx,[a.shoulder,a.elbow,a.wrist]);ctx.stroke();
  ctx.strokeStyle=profile.skin;ctx.lineWidth=23;path(ctx,[a.shoulder,a.elbow,a.wrist]);ctx.stroke();
  const sleeve=add(a.shoulder,mul(sub(a.elbow,a.shoulder),.42));ctx.strokeStyle=profile.shirt;ctx.lineWidth=32;path(ctx,[a.shoulder,sleeve]);ctx.stroke();
 }
 const hand=(points)=>{
  if(!points.length)return;
  ctx.fillStyle=profile.skin;ctx.strokeStyle=profile.shade;ctx.lineWidth=1.2;path(ctx,[0,1,5,9,13,17].map(i=>points[i]),true);ctx.fill();ctx.stroke();
  for(const chain of fingers){ctx.strokeStyle=profile.shade;ctx.lineWidth=7;path(ctx,chain.map(i=>points[i]));ctx.stroke();ctx.strokeStyle=profile.skin;ctx.lineWidth=5;path(ctx,chain.map(i=>points[i]));ctx.stroke();}
  if(options.joints){for(let i=0;i<points.length;i++){ctx.beginPath();ctx.arc(...points[i],1.8,0,Math.PI*2);ctx.fillStyle='#124a63';ctx.fill();}}
 };
 const allHands=()=>{const order=options.front==='left'?['right','left']:['left','right'];for(const name of order)hand(p.hands[name]);};
 if(options.layer==='behind')allHands();
 const oval=faceOval.map(i=>p.face[i]).filter(Boolean);
 if(oval.length){
  const xs=oval.map(v=>v[0]),ys=oval.map(v=>v[1]),cx=(Math.min(...xs)+Math.max(...xs))/2,top=Math.min(...ys),bottom=Math.max(...ys);
  ctx.strokeStyle=profile.skin;ctx.lineWidth=30;path(ctx,[[cx,bottom-3],[250,260]]);ctx.stroke();
  ctx.fillStyle=profile.skin;ctx.strokeStyle=profile.shade;ctx.lineWidth=1.3;path(ctx,oval,true);ctx.fill();ctx.stroke();
  ctx.fillStyle=profile.hair;ctx.beginPath();ctx.ellipse(cx,top+10,(Math.max(...xs)-Math.min(...xs))*.54,18,0,Math.PI,Math.PI*2);ctx.fill();
  for(let i=0;i<features.length;i++){const points=features[i].map(k=>p.face[k]).filter(Boolean);ctx.strokeStyle=i<2?'#743d48':'#3b3433';ctx.lineWidth=i<2?1.4:1.8;path(ctx,points);ctx.stroke();}
 }
 if(options.layer!=='behind')allHands();
 if(p.contact){ctx.strokeStyle='#b33497';ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(...p.contact,5,0,Math.PI*2);ctx.stroke();}
 if(options.joints){for(const a of Object.values(p.arms)){ctx.fillStyle='#124a63';for(const v of [a.shoulder,a.elbow,a.wrist]){ctx.beginPath();ctx.arc(...v,3,0,Math.PI*2);ctx.fill();}}}
 return {...p,milliseconds:performance.now()-start};
}
return {ik,setup,pose,draw,profiles,distance};
})();
