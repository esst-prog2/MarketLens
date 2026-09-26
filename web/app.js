"use strict";
const $ = (id) => document.getElementById(id);
const money = (n) => n == null ? "Unavailable" : new Intl.NumberFormat("en-US", {style:"currency",currency:"USD",maximumFractionDigits:2}).format(n);
const percent = (n) => n == null ? "—" : `${(n * 100).toFixed(1)}%`;
const dateLabel = (d) => d ? new Date(`${d.slice(0,10)}T12:00:00Z`).toLocaleDateString("en-US", {month:"short",day:"numeric",year:"numeric",timeZone:"UTC"}) : "Unavailable";
const escapeHTML = (s) => String(s ?? "—").replace(/[&<>"']/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
let mode = "current";
let state = null;
let busy = false;

function chart(values, className, color, label) {
  const lo = Math.min(...values), hi = Math.max(...values);
  const points = values.map((v,i) => `${(i / Math.max(1,values.length-1)*500).toFixed(2)},${(85-(v-lo)/Math.max(hi-lo,0.01)*70).toFixed(2)}`).join(" ");
  return `<svg class="${className}" viewBox="0 0 500 100" preserveAspectRatio="none" role="img" aria-label="${label}"><path d="M0 94 H500" stroke="#2b3445" stroke-dasharray="3 5"/><polyline points="${points}" fill="none" stroke="${color}" stroke-width="2.5" vector-effect="non-scaling-stroke"/>${values.length===1?'<circle cx="0" cy="85" r="3" fill="'+color+'"/>':""}</svg>`;
}

function controls() {
  $("advance").disabled = busy || !state || state.remaining === 0;
  $("invest").disabled = busy || !state || !!state.portfolio;
  $("profile").disabled = busy || !!state?.portfolio;
  $("balance").disabled = busy || !!state?.portfolio;
  $("reset").disabled = busy || !state;
  if (state?.mode) {
    $("advance").disabled ||= state.mode !== "replay";
    $("invest").disabled ||= !state.can_invest || state.mode === "legacy";
    $("reset").disabled ||= state.mode === "legacy";
  }
  if ($("data-mode")) $("data-mode").disabled = busy;
}

async function request(path, body) {
  if (busy) return;
  busy = true; controls(); $("error").hidden = true;
  try {
    if (body === undefined) path += `?mode=${mode}`;
    else body = {...body, mode};
    const response = await fetch(path, body === undefined ? {} : {method:"POST", headers:{"Content-Type":"application/json"},body:JSON.stringify(body)});
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "The request could not be completed.");
    state = data; render();
    $("status").textContent = `Market data as of ${dateLabel(state.date)}. ${state.portfolio ? `Portfolio value ${money(state.portfolio.value)}.` : "Choose a profile to start your portfolio."}`;
  } catch (error) {
    $("error").textContent = error.message || "Cannot connect to MarketLens. Check that the Python server is running.";
    $("error").hidden = false;
  } finally {busy = false; controls();}
}

function renderAllocation() {
  if (!state) return;
  const weights = state.profiles[$("profile").value];
  $("allocation").innerHTML = `<div class="allocation-bar" aria-hidden="true">${Object.values(weights).map(w=>`<span style="width:${w*100}%"></span>`).join("")}</div><div class="allocation-labels">${Object.entries(weights).map(([s,w])=>`<span>${s} <b>${Math.round(w*100)}%</b></span>`).join("")}</div>`;
}

function render() {
  if (state.training) {renderMVP(); return;}
  if (state.mode === "legacy") {
    $("training").innerHTML = "Legacy heuristic results ? no trained probability model.";
    $("provider-status").textContent = "Read-only legacy 2024 replay ? heuristic strength is not probability";
    $("advance").hidden = true;
    document.querySelector(".replay-note").textContent = "Preserved original experiment ? read-only";
  }
  $("as-of").textContent = `As of ${dateLabel(state.date)}`;
  $("advance").innerHTML = state.remaining ? 'Next trading day <span aria-hidden="true">→</span>' : "Sample complete";
  $("history-count").textContent = state.history.length;
  $("signals").innerHTML = state.signals.map((s,i)=>`<article class="market-card"><div class="asset-title"><span class="asset-icon" aria-hidden="true">${["↗","▥","◇"][i]}</span><div><h3>${s.name}</h3><span class="ticker">${s.symbol} · ${s.description}</span></div></div><div class="price-row"><span class="price">${money(s.price)}</span><span class="muted">USD / CLOSE</span></div>${chart(s.chart,"sparkline",["#9bbbf4","#b5a0ff","#efc77a"][i],`${s.name}: last 20 trading days, ${percent(s.momentum)} change`)}<div class="signal-row"><span class="direction ${s.direction.toLowerCase()}">${s.direction === "Up" ? "↗" : s.direction === "Down" ? "↘" : "→"} ${s.direction} outlook</span><span class="risk">${s.risk} recent risk</span></div><div class="strength"><span>Signal strength</span><b>${s.strength} / 100</b></div><div class="meter" aria-hidden="true"><span style="width:${s.strength}%"></span></div><p class="explanation">${s.explanation}</p></article>`).join("");
  const p = state.portfolio;
  if (p) {
    $("profile").value = p.profile; $("balance").value = p.initial;
    $("invest").textContent = "Allocation applied";
    $("portfolio").innerHTML = `<div class="portfolio-meta">${p.profile} profile · started with ${money(p.initial)}</div><div class="portfolio-value">${money(p.value)}</div><div class="${p.profit>=0?'gain':'loss'}">${p.profit>=0?'+':''}${money(p.profit)} <span>(${percent(p.return)})</span> <span class="portfolio-meta">since ${dateLabel(p.started)}</span></div>${chart(p.chart.map(x=>x.value),"portfolio-chart",p.profit>=0?"#75ddba":"#f1a2a9","Portfolio value over the replay period")}<div class="chart-labels"><span>${dateLabel(p.started)}</span><span>${dateLabel(state.date)}</span></div><div class="holdings">${p.holdings.map(h=>`<div class="holding"><span>${h.name}<small>${percent(h.weight)}</small></span><span>${money(h.value)}</span></div>`).join("")}</div>`;
  } else {
    $("invest").innerHTML = 'Apply model allocation <span aria-hidden="true">↗</span>';
    $("portfolio").innerHTML = '<div class="empty-state"><div class="empty-icon" aria-hidden="true">◈</div><h3>A fresh perspective starts here.</h3><p>Apply an allocation to put your virtual money to work. Then advance the clock to see how it performs.</p></div>';
  }
  renderAllocation();
  const m = state.performance;
  $("metrics").innerHTML = `<div class="metric"><div class="metric-label">Model directional accuracy</div><div class="metric-value">${m.accuracy===null?'—':percent(m.accuracy)}</div><div class="metric-detail">${m.evaluated} evaluated forecasts</div></div><div class="metric"><div class="metric-label">Always-up baseline</div><div class="metric-value">${m.always_up===null?'—':percent(m.always_up)}</div><div class="metric-detail">Same assets, dates and horizon</div></div><div class="metric"><div class="metric-label">Awaiting an outcome</div><div class="metric-value">${m.pending}</div><div class="metric-detail">Advance the historical clock to evaluate</div></div>`;
  $("history-rows").innerHTML = state.history.map(h=>`<tr><td>${dateLabel(h.date)}</td><td>${h.symbol}</td><td>${h.direction}</td><td>${h.due?dateLabel(h.due):'Beyond sample'}</td><td>${h.return===null?'—':`${h.actual} (${percent(h.return)})`}</td><td class="${h.correct===true?'gain':h.correct===false?'loss':'muted'}">${h.correct===null?(h.due?'Pending':'Beyond sample'):h.correct?'Correct':'Incorrect'}</td></tr>`).join("");
  if (typeof renderJourney === "function") renderJourney();
}

$("profile").addEventListener("change", renderAllocation);
$("setup-form").addEventListener("submit", e=>{e.preventDefault();request("/api/portfolio", {profile:$("profile").value,balance:Number($("balance").value)});});
$("advance").addEventListener("click", ()=>request("/api/advance", {}));
$("reset").addEventListener("click", ()=>{if(confirm(`Reset ${mode} mode? This clears its virtual portfolio, model versions and forecast history. Other modes and learning preferences are preserved.`)) request("/api/reset", {});});
$("method-button").addEventListener("click",()=>{$("methodology").open=true;$("methodology").scrollIntoView({behavior:matchMedia("(prefers-reduced-motion: reduce)").matches?"instant":"smooth"});});
request("/api/state");
