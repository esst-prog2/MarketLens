"use strict";

function metric(label, value, detail="") {
  return `<div class="metric"><div class="metric-label">${label}</div><div class="metric-value">${value}</div><div class="metric-detail">${detail}</div></div>`;
}
function quoteDetails(q) {
  return q ? `${escapeHTML(q.status)} · ${escapeHTML(q.source)}<br>Observed: ${escapeHTML(q.observed_at)}<br>Fetched: ${escapeHTML(q.fetched_at || "frozen replay")}` : "Unavailable · awaiting provider data";
}
function trackRecord(f) {
  const t=f.track_record;
  const measured=t.hit_rate===null ? `Not enough history yet (${t.count} of ${t.minimum} earlier calls)` : `${percent(t.hit_rate)} of ${t.count} earlier calls like this were right`;
  return `${escapeHTML(f.direction)} · ${measured}<br><small>Model estimate ${percent(f.confidence)} (uncalibrated; band ${percent(t.low)}–${percent(t.high)})</small>`;
}
function forecastCard(f, horizon) {
  if (!f) return `<div class="forecast"><h4>${horizon === 5 ? "Five-session direction" : "Next-session close"}</h4><p>No eligible model forecast yet.</p></div>`;
  return `<div class="forecast"><h4>${horizon === 5 ? "Five-session direction" : "Next-session close"}</h4><strong>${horizon === 5 ? trackRecord(f) : money(f.estimate)}</strong><p>Reference ${dateLabel(f.date)} · ${money(f.price)}<br>Target ${dateLabel(f.due)}</p><small>Issued ${escapeHTML(f.issued_at)}<br>${escapeHTML(f.model)}</small></div>`;
}
function renderMVP() {
  $("data-mode").value = state.mode;
  $("as-of").textContent = `${state.mode === "replay" ? "REPLAY" : "Completed daily history"} · ${dateLabel(state.date)}`;
  document.querySelector(".replay-note").textContent = state.mode === "replay" ? "Frozen real prices · offline simulated clock" : "Quotes update independently of daily forecasts";
  $("advance").hidden = state.mode !== "replay";
  $("advance").textContent = state.remaining ? "Next trading day →" : "Sample complete";
  $("reset").textContent = `Reset ${state.mode} experiment`;
  $("history-count").textContent = state.history.length;
  $("provider-status").innerHTML = state.mode === "replay" ? "Historical replay · no network required · 2022 warm-up, practice 2023 to 2 Nov 2026" : `Current data · market ${state.market.open ? "open" : "closed"} · ${escapeHTML(state.provider.status)}<br><small>Latest completed exchange session: ${escapeHTML(state.market.latest_completed)}. Next refresh: ${escapeHTML(state.provider.next_attempt)}. ${(state.provider.errors || []).map(escapeHTML).join(" · ")}</small>`;
  $("signals").innerHTML = state.signals.map((s,i)=>`<article class="market-card"><div class="asset-title"><div><h3>${s.name}</h3><span class="ticker">${s.symbol} · ${s.description}</span></div></div><div class="price-row"><span class="price">${money(s.price)}</span><span class="muted">USD</span></div><p class="quote-details">${quoteDetails(s.quote)}</p>${s.chart.length ? chart(s.chart,"sparkline",["#9bbbf4","#b5a0ff","#efc77a"][i],`${s.symbol}: completed daily closes`) : ""}<p class="muted">${s.risk} recent volatility. Trailing 20-session change: ${percent(s.momentum)}. The model combines recent returns and volatility; it can disagree with this trend.</p>${forecastCard(s.forecast,5)}${forecastCard(s.price_forecast,1)}</article>`).join("");
  const p=state.portfolio;
  $("invest").textContent = p ? "Allocation applied" : state.can_invest ? "Apply fixed allocation ↗" : "Waiting for three usable quotes";
  if(p) {
    $("profile").value=p.profile; $("balance").value=p.initial;
    $("portfolio").innerHTML=`<div class="portfolio-meta">${p.profile} · started with ${money(p.initial)} · ${p.fresh ? "Usable quotes" : "Cached / partial valuation — inspect timestamps"}</div><div class="portfolio-value">${money(p.value)}</div><p class="${p.profit>=0?'gain':'loss'}">${money(p.profit)} (${percent(p.return)}) since ${dateLabel(p.started)}</p>${chart(p.chart.map(x=>x.value),"portfolio-chart","#75ddba","Observed virtual portfolio value")}<div class="holdings">${p.holdings.map(h=>`<div class="holding"><span>${h.name}<small>${h.units.toFixed(6)} units · ${percent(h.weight)}<br>${escapeHTML(h.status)} · ${escapeHTML(h.observed_at)}<br>Entry ${money(h.entry.price)} · ${escapeHTML(h.entry.observed_at)}</small></span><span>${money(h.value)}</span></div>`).join("")}</div>`;
  } else $("portfolio").innerHTML='<div class="empty-state"><h3>Try a fixed allocation.</h3><p>Use a virtual balance from $100 to $1,000,000. Current-data entry needs usable quotes for all three assets. Replay has its own independent portfolio.</p></div>';
  renderAllocation();
  const m=state.performance;
  $("metrics").innerHTML=metric("Five-session accuracy",percent(m.accuracy),`${m.evaluated} evaluated directions`)+metric("Always-Up / momentum",`${percent(m.always_up)} / ${percent(m.momentum)}`,"Same direction observations")+metric("Next-close MAE",money(m.mae),`${m.price_evaluated} evaluated prices · MAPE ${percent(m.mape)}`)+metric("Last-close baseline MAE",money(m.last_close_mae),"Lower MAE is better; the baseline may win")+metric("Selected-direction Brier",m.brier===null?"—":m.brier.toFixed(4),"Lower is better · (probability − correctness)²")+metric("Pending",m.pending,"Outcomes appear only after their target session");
  $("history-rows").innerHTML=state.history.map(h=>`<tr><td>${dateLabel(h.date)}<small>${escapeHTML(h.model)}<br>Issued ${escapeHTML(h.issued_at)}</small></td><td>${h.symbol}</td><td>${h.horizon===5?`${h.direction} · ${percent(h.confidence)}<small>5 sessions</small>`:`${money(h.estimate)}<small>Next close</small>`}</td><td>${dateLabel(h.due)}</td><td>${h.actual_close===null?'Pending':money(h.actual_close)+(h.horizon===5?` · ${h.actual} (${percent(h.return)})`:'')}</td><td class="${h.correct===false?'loss':h.correct===true?'gain':'muted'}">${h.actual_close===null?'Pending':h.horizon===5?(h.correct?'Correct':'Incorrect'):`Error ${money(h.error)} (${percent(h.ape)})`}</td></tr>`).join("");
  renderContenders();
  renderTraining();
  if(typeof renderJourney === "function") renderJourney();
}
const CONTENDER_COLORS={"always-up":"#efc77a","momentum-20":"#b5a0ff","last-close":"#9aa7be"};
function contenderColor(name, model) { return name===model ? "#75ddba" : CONTENDER_COLORS[name] || "#9aa7be"; }
function edgeLine(e, label, unit) {
  if(!e) return "";
  const show=unit==="points" ? v=>`${v>=0?"+":""}${(v*100).toFixed(1)} points` : v=>`${v>=0?"+":"−"}${money(Math.abs(v))}`;
  const range=e.low===null ? `Not enough history yet (${e.sessions} of ${e.minimum} shared sessions)` : `${show(e.value)} (approx. 95% range ${show(e.low)} to ${show(e.high)}) over ${e.sessions} sessions: <strong>${escapeHTML(e.verdict)}</strong>`;
  return `<p class="edge">${label} against ${escapeHTML(e.against)}: ${range}</p>`;
}
function rollingChart(lines, model) {
  const names=Object.keys(lines).filter(n=>lines[n].length);
  if(!names.length) return '<p class="muted">The 20-session accuracy chart appears after 20 shared sessions have matured.</p>';
  const dates=lines[names[0]].map(p=>p.date), x=i=>(i/Math.max(1,dates.length-1)*500).toFixed(2), y=v=>(95-v*90).toFixed(2);
  // The model is drawn first and thicker, so a baseline with identical accuracy stays visible on top.
  const paths=[...names].sort((a,b)=>(b===model)-(a===model)).map(n=>`<polyline points="${lines[n].map((p,i)=>`${x(i)},${y(p.accuracy)}`).join(" ")}" fill="none" stroke="${contenderColor(n,model)}" stroke-width="${n===model?3:2}" vector-effect="non-scaling-stroke"/>`).join("");
  return `<div class="rolling-wrap"><div class="rolling-axis" aria-hidden="true"><span>100%</span><span>50%</span><span>0%</span></div><svg class="rolling-chart" viewBox="0 0 500 100" preserveAspectRatio="none" role="img" aria-label="Accuracy over the latest 20 sessions, per contender, ${escapeHTML(dates[0])} to ${escapeHTML(dates[dates.length-1])}"><path d="M0 50 H500" stroke="#5b6680" stroke-dasharray="4 4" vector-effect="non-scaling-stroke"/><path d="M0 5 H500 M0 95 H500" stroke="#283042" vector-effect="non-scaling-stroke"/>${paths}</svg></div><div class="legend">${names.map(n=>`<span><i style="background:${contenderColor(n,model)}"></i>${escapeHTML(n)}</span>`).join("")}<span>dashed line: 50% · ${dateLabel(dates[0])} – ${dateLabel(dates[dates.length-1])}</span></div>`;
}
function renderContenders() {
  const c=state.contenders, cell=(n,v)=>n?v:"—";
  $("contenders").innerHTML=`<h3>Contenders side by side</h3><p class="muted">Every contender's forecasts are stored when issued and scored only on the observations all of them answered. A baseline that has no answer for a horizon shows a dash.</p><div class="table-scroll"><table><thead><tr><th>Contender</th><th>5-session calls</th><th>Accuracy</th><th>Brier</th><th>Next-close estimates</th><th>MAE</th></tr></thead><tbody>${c.board.map(b=>`<tr class="${b.name===c.model?"model-row":""}"><td>${escapeHTML(b.name)}</td><td>${b.calls}</td><td>${cell(b.calls,percent(b.accuracy))}</td><td>${b.brier===null?"—":b.brier.toFixed(4)}</td><td>${b.estimates}</td><td>${cell(b.estimates,money(b.mae))}</td></tr>`).join("")}</tbody></table></div>${edgeLine(c.edge["5"],"Direction accuracy of the model","points")}${edgeLine(c.edge["1"],"Next-close error of the model","money")}<p class="muted">The range is approximate: sessions are grouped in blocks of five because overlapping five-session targets are not independent. A verdict other than “no measurable difference” needs the whole range on one side of zero.</p><h3>Accuracy over the latest 20 sessions</h3>${rollingChart(c.rolling,c.model)}`;
}
function comparisonList(all, render) {
  // Complete comparisons and the newest one in progress stay visible; the rest fold away.
  const open=all.filter((c,i)=>c.status==="complete" || i===all.findIndex(x=>x.status!=="complete"));
  const rest=all.filter(c=>!open.includes(c));
  return open.map(render).join("")+(rest.length?`<details class="more-comparisons"><summary>${rest.length} more in progress or pending</summary>${rest.map(render).join("")}</details>`:"");
}
function renderTraining() {
  const t=state.training, a=t.active;
  $("training").innerHTML=`<h3>Automatic daily retraining</h3><p>${a?`Active ${escapeHTML(state.model)}<br>Cutoff ${a.cutoff} · fit ${a.fit_start}–${a.fit_end} (${a.fit_sessions} sessions), last fit label ${a.fit_label_end}; calibration ${a.cal_start}–${a.cal_end} (${a.cal_sessions} sessions).`:'No model yet: waiting for sufficient complete shared daily history.'}</p><p>Latest run: ${escapeHTML(t.runs[0]?.status || "waiting for history")} ${escapeHTML(t.runs[0]?.error || "")}<br>Class counts (fit / calibration): ${a ? escapeHTML(JSON.stringify(a.classes)) + " / " + escapeHTML(JSON.stringify(a.cal_classes)) : "Unavailable"}. Missing Up/Down coverage or a previously unseen calibration class blocks a new version. A fitted Flat class is retained with sigmoid smoothing even if this calibration window has zero Flat examples; its reliability is unproven.</p><p class="muted">Runs while the app is open; startup catches up to the latest available session. Old forecasts and holdings stay fixed.</p><details><summary>Recent training runs (${t.runs.length})</summary>${t.runs.map(r=>`<p>${r.cutoff} · ${escapeHTML(r.status)} · ${escapeHTML(r.finished || r.started)}${r.error?`<br>${escapeHTML(r.error)}`:''}</p>`).join('')}</details><label for="metric-version">Probability reliability / version metrics</label><select id="metric-version"><option value="all">All main forecasts in ${state.mode} mode</option>${Object.keys(state.versions).map(v=>`<option value="${escapeHTML(v)}">${escapeHTML(v)}</option>`).join('')}</select><div id="reliability"></div><h3>Frozen-version comparisons</h3><p class="muted">Consecutive versions make shadow predictions on the same next 20 reference sessions (60 directions and 60 prices each). Both models remain frozen. This is separate from the main daily forecasts; improvement is not guaranteed.</p>${t.comparisons.length?comparisonList(t.comparisons,c=>`<details class="comparison" data-status="${c.status}"><summary>${c.start}–${c.end} · ${c.status} · ${c.newer_metrics.evaluated}/60 direction outcomes</summary><p>Older: ${escapeHTML(c.older)}<br>Newer: ${escapeHTML(c.newer)}<br>Final direction outcome due ${c.due}</p><div class="table-scroll"><table><thead><tr><th>Version</th><th>Accuracy</th><th>Price MAE / MAPE</th><th>Brier</th><th>Up / momentum baselines</th><th>Last-close MAE</th><th>Prices</th></tr></thead><tbody>${[['Older',c.older_metrics],['Newer',c.newer_metrics]].map(([n,m])=>`<tr><td>${n}</td><td>${percent(m.accuracy)}</td><td>${money(m.mae)} / ${percent(m.mape)}</td><td>${m.brier===null?"?":m.brier.toFixed(4)}</td><td>${percent(m.always_up)} / ${percent(m.momentum)}</td><td>${money(m.last_close_mae)}</td><td>${m.price_evaluated}/60</td></tr>`).join('')}</tbody></table></div></details>`):'<p>Pending: a second successful model version is needed.</p>'}`;
  $("metric-version").addEventListener("change",renderReliability); renderReliability();
}
function renderReliability() {
  const m=$("metric-version").value === "all" ? state.performance : state.versions[$("metric-version").value];
  $("reliability").innerHTML=`<p>${m.evaluated} directions · accuracy ${percent(m.accuracy)} · always-Up ${percent(m.always_up)} · momentum ${percent(m.momentum)} · Brier ${m.brier===null?'—':m.brier.toFixed(4)}<br>${m.price_evaluated} prices · MAE ${money(m.mae)} · MAPE ${percent(m.mape)} · last-close MAE ${money(m.last_close_mae)}</p><div class="table-scroll"><table><thead><tr><th>Probability bin</th><th>Count</th><th>Mean prediction</th><th>Observed accuracy</th></tr></thead><tbody>${m.bins.map((b,i)=>`<tr><td>${percent(b.low)}–${percent(b.high)}${i===4?' inclusive':' (upper excluded)'}</td><td>${b.count}</td><td>${percent(b.confidence)}</td><td>${percent(b.accuracy)}</td></tr>`).join('')}</tbody></table></div><p class="muted">Small samples are uncertain. Overlapping five-session targets are not independent. A calibrated estimate is not a guarantee.</p>`;
}
$("data-mode").addEventListener("change",async ()=>{const previous=mode; mode=$("data-mode").value;await request("/api/state");if(state?.mode!==mode){mode=previous;$("data-mode").value=previous;}});
$("refresh").addEventListener("click",()=>request("/api/refresh",{}));
setInterval(()=>{if(!busy && mode==="current" && !document.hidden) request("/api/state");},15000);
