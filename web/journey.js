"use strict";

// Educational routing, not a financial suitability assessment.
const SOURCES = {
  allocation: ["Investor.gov · Asset allocation & diversification", "https://www.investor.gov/introduction-investing/getting-started/asset-allocation"],
  risk: ["Investor.gov · Gauge your risk tolerance", "https://www.investor.gov/introduction-investing/investing-basics/save-and-invest/gauge-your-risk-tolerance"],
  etf: ["Investor.gov · Exchange-traded funds", "https://www.investor.gov/introduction-investing/general-resources/news-alerts/alerts-bulletins/investor-bulletins-24"],
  bonds: ["FINRA · Bonds", "https://www.finra.org/investors/investing/investment-products/bonds"],
  gold: ["State Street · SPDR Gold Shares", "https://www.ssga.com/us/en/individual/etfs/spdr-gold-shares-gld"],
  dca: ["Investor.gov · Dollar-cost averaging", "https://www.investor.gov/introduction-investing/investing-basics/glossary/dollar-cost-averaging"],
};
const LESSONS = [
  {id:"risk",title:"What kind of risk can you live with?",topic:"foundations",level:"beginner",minutes:3,description:"Separate what you know from how much uncertainty you can tolerate.",source:"risk",sections:[
    ["Knowledge and comfort are different", "Experience describes your familiarity with investing. Risk tolerance describes your willingness to accept losses and uncertainty. Learning more does not oblige you to choose a more aggressive portfolio."],
    ["Put a loss into numbers", "In a hypothetical 15% decline, a $10,000 portfolio becomes $8,500. Would you need the money soon? Would that loss change your plans? This is a reflection exercise, not a forecast or the largest possible loss."],
    ["Try this", "Write down when you expect to need the money and what a loss would prevent you from doing. MarketLens uses your answers to order educational examples; it does not assess your complete finances."]]},
  {id:"diversification",title:"One portfolio. Different moving parts.",topic:"foundations",level:"beginner",minutes:3,description:"Understand allocation, diversification and why three assets can behave differently.",source:"allocation",sections:[
    ["Start with the mix", "Allocation describes how money is divided among investments. Diversification spreads exposure so that one investment does not determine the entire outcome. Different assets can still fall together."],
    ["Read a model portfolio", "The Balanced example allocates 50% to an equity ETF, 35% to a Treasury ETF and 15% to a gold trust. These are transparent teaching weights, not an optimized mix. Changing the weights changes the exposures."],
    ["Try this", "Compare the three portfolio examples. Identify which has the most exposure to equity prices and which has the most exposure to Treasury bond prices."]]},
  {id:"etfs",title:"Stocks & ETFs, without the jargon",topic:"stocks",level:"beginner",minutes:3,description:"Learn what a fund share represents before following a price chart.",source:"etf",sections:[
    ["A share of a basket", "An ETF holds a portfolio of assets and trades on an exchange. Buying a fund share gives exposure to that portfolio. A narrow fund may still be highly concentrated; the label ETF does not mean low risk."],
    ["Our equity example", "MarketLens uses SPY as a proxy for US large-company shares. Its price is not a prediction of the whole economy. The fund has costs, and its market price can differ from the value of its underlying assets."],
    ["Try this", "Open Explore markets and inspect SPY. Separate the observed price change from the model's expectation for the next five trading days. One is an observation; the other can be wrong."]]},
  {id:"bonds",title:"Why can a bond fund lose value?",topic:"bonds",level:"beginner",minutes:3,description:"Meet interest-rate risk and the difference between a bond and a bond fund.",source:"bonds",sections:[
    ["An IOU with a market price", "A bond represents borrowing. Its market value can change before maturity. When market interest rates rise, existing bond prices generally fall. Longer-maturity bonds can be more sensitive to those moves."],
    ["A Treasury ETF is not cash", "IEF holds US Treasury bonds with 7–10 year maturities. It can lose market value even though it holds government debt. Our bond-heavy example is not a capital guarantee or a savings-account substitute."],
    ["Try this", "Watch IEF over several replay days. Compare its price movement with SPY rather than assuming the bond fund must always move in the opposite direction."]]},
  {id:"gold",title:"Where does gold fit?",topic:"gold",level:"beginner",minutes:2,description:"Explore a gold-backed trust and the limits of a familiar asset.",source:"gold",sections:[
    ["Exposure through a trust", "GLD seeks to reflect the price of gold bullion, less expenses. Holding its shares is different from keeping physical gold yourself. The issuer describes how the trust holds gold and pays its expenses."],
    ["No income promise", "GLD does not generate income. Its price can move down as well as up, and the trust sells some gold to cover expenses. Adding gold to an example portfolio does not guarantee protection during a market decline."],
    ["Try this", "Compare a few gold and equity price movements in the replay. A short sample can illustrate differences but cannot establish a reliable future relationship."]]},
  {id:"buyhold",title:"Buy, hold, observe",topic:"strategies",level:"beginner",minutes:3,description:"A simple practice framework: choose a mix and keep the holdings fixed.",source:"allocation",sections:[
    ["Make the experiment explicit", "In this demo, you select an allocation and buy fractional units at the selected mode?s observed prices. The holdings remain fixed as the clock moves forward. This lets you see price effects without mixing in repeated trading decisions."],
    ["What to observe", "Watch total value, individual holdings and how portfolio weights drift. Prices do not move together. A larger equity allocation can make equity movements more influential; a larger bond allocation increases bond exposure."],
    ["What this experiment leaves out", "The trained replay uses 2022 for warm-up and 2023?2024 for practice and excludes distributions, costs and taxes. It cannot demonstrate a long-term result or reproduce a complete investment strategy. Use it to understand the mechanics."]]},
  {id:"dca",title:"Investing at regular intervals",topic:"strategies",level:"intermediate",minutes:3,description:"Understand dollar-cost averaging with a small worked example.",source:"dca",sections:[
    ["A schedule rather than a price guess", "Dollar-cost averaging means investing equal amounts on a regular schedule. An equal cash amount buys more units at a lower price and fewer at a higher price."],
    ["Work through the arithmetic", "Investing $100 at $10 per unit buys 10 units. Another $100 at $20 buys 5 units. You now hold 15 units for $200: an average cost of about $13.33 per unit. Future profit still depends on future prices."],
    ["Explore before simulating", "Regular contributions are not implemented in the current replay. The Practice section invests one starting balance once. This lesson explains a different approach, without implying that the simulator executes it."]]},
  {id:"rebalance",title:"When a portfolio drifts",topic:"strategies",level:"intermediate",minutes:3,description:"See how rebalancing differs from simply holding your initial units.",source:"allocation",sections:[
    ["Weights change", "If one holding grows faster, it becomes a larger part of the portfolio. Rebalancing adjusts holdings toward chosen target weights. It can involve selling some assets and buying others."],
    ["A question to investigate", "Compare a calendar-based review with a rule that checks for a chosen amount of drift. Ask how frequently each would trade and what costs those trades would create. Neither is a promise of a better return."],
    ["Current practice mode", "The replay shows changing weights but does not rebalance. You can observe drift here; testing rebalancing rules requires an additional simulator. Resetting a replay is not a rebalance."]]},
  {id:"signals",title:"A signal is not a promise",topic:"strategies",level:"advanced",minutes:4,description:"Read calibrated forecasts critically and compare them with a basic benchmark.",sections:[
    ["What this model actually does", "MarketLens fits a classifier on completed historical prices and calibrates its direction probabilities on a later window. It predicts Up or Down after five trading sessions. A separate regression estimates the next-session USD close. Confidence is a model estimate, not a promise; the original momentum rule remains a comparison baseline."],
    ["Look for mistakes", "In Model history, forecasts remain pending until their outcome date. Correct and incorrect calls both remain visible. The always-up benchmark uses the same assets and dates, making it a useful first comparison."],
    ["Accuracy is not profit", "Directional accuracy ignores the size of wins and losses and the cost of trading. Overlapping forecast windows share price movements. The model neither places trades nor adjusts the example portfolios."]]},
];
const TOPICS = {foundations:"Foundations",stocks:"Stocks & ETFs",bonds:"Bonds",gold:"Gold",strategies:"Strategies"};
const GOALS = {learn:"Learn the basics",explore:"Explore markets",practice:"Practise investing"};
const LEVELS = {beginner:"Starting out",intermediate:"Know the basics",advanced:"More experienced"};
const RISKS = {cautious:"Cautious",balanced:"Balanced",adventurous:"Comfortable with larger swings"};
const MIXES = {
  Conservative:{title:"Bond-focused",tag:"More Treasury exposure",description:"Explore a mix with a smaller equity allocation and a larger Treasury bond allocation.",tradeoff:"Interest-rate movements can hurt bond funds. A bond-heavy mix can still lose money.",weights:[20,65,15]},
  Balanced:{title:"A balanced starting point",tag:"A mix of three markets",description:"Observe how equities, Treasury bonds and gold contribute to one portfolio.",tradeoff:"Diversification cannot prevent all losses. The three holdings can fall together.",weights:[50,35,15]},
  Growth:{title:"Equity-focused",tag:"More equity exposure",description:"Explore how a larger share of equities changes the path of a virtual portfolio.",tradeoff:"Equity declines have a larger impact on this mix. Higher risk does not guarantee higher returns.",weights:[75,15,10]},
};
const STORAGE_KEY = "marketlens.journey.v1";
let journey = null, savedLessons = [], completedLessons = [];
let currentPage = "discover", wizardStep = 0, draft = {};

function validJourney(p) {
  return p && Object.hasOwn(GOALS,p.goal) && Object.hasOwn(LEVELS,p.level) && Object.hasOwn(RISKS,p.risk) && ["short","medium","long"].includes(p.horizon) && Array.isArray(p.topics) && p.topics.length>0 && p.topics.every(t=>Object.hasOwn(TOPICS,t));
}
function storageNotice() { $("storage-message").hidden=false; $("storage-message").textContent="Your browser could not save these preferences. You can continue, but changes may be lost when you reload."; }
try {
  const stored = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
  if (validJourney(stored?.profile)) journey=stored.profile;
  const validIds = new Set(LESSONS.map(l=>l.id));
  savedLessons = Array.isArray(stored?.saved) ? [...new Set(stored.saved.filter(id=>validIds.has(id)))] : [];
  completedLessons = Array.isArray(stored?.completed) ? [...new Set(stored.completed.filter(id=>validIds.has(id)))] : [];
} catch { storageNotice(); }
function saveJourney() { try { localStorage.setItem(STORAGE_KEY,JSON.stringify({profile:journey,saved:savedLessons,completed:completedLessons})); } catch {storageNotice();} }

function choice(name,value,title,description,type="radio") {
  const checked = type==="checkbox" ? draft.topics.includes(value) : draft[name]===value;
  return `<label class="choice"><input type="${type}" name="${name}" value="${value}" ${checked?'checked':''}><span><strong>${title}</strong>${description?`<small>${description}</small>`:''}</span><span class="choice-check" aria-hidden="true">✓</span></label>`;
}
function startWizard() {
  draft=journey?{...journey,topics:[...journey.topics]}:{goal:"",topics:[],level:"",risk:"",horizon:""};
  wizardStep=0; $("workspace").hidden=true; $("onboarding").hidden=false; $("wizard-cancel").hidden=!journey;
  drawWizard();
}
function drawWizard() {
  $("wizard-error").hidden=true;
  $("wizard-progress").innerHTML=["Your interests","Your experience","Your comfort zone"].map((name,i)=>`<span class="${i<=wizardStep?'reached':''}" ${i===wizardStep?'aria-current="step"':''}>${i+1} <small>${name}</small></span>`).join("");
  const headings=["What brings you here?","Where are you starting from?","How do you feel about risk?"];
  let body="";
  if(wizardStep===0) body=`<fieldset><legend>Choose your main goal</legend>${choice('goal','learn','I want to learn','Build confidence with short, practical explainers.')}${choice('goal','explore','I want to explore','Understand markets and compare different approaches.')}${choice('goal','practice','I want to practise investing','Try a portfolio with virtual money.')}</fieldset><fieldset><legend>What would you like to explore? <small>Choose at least one</small></legend><div class="topic-choices">${Object.entries(TOPICS).map(([k,v])=>choice('topics',k,v,'','checkbox')).join('')}</div></fieldset>`;
  if(wizardStep===1) body=`<p class="muted">This changes where your learning path starts. It does not determine how much risk you should take.</p><fieldset><legend>Your investing experience</legend>${choice('level','beginner','I’m starting out','Explain the terms and show me the fundamentals.')}${choice('level','intermediate','I know the basics','Help me compare allocations and strategies.')}${choice('level','advanced','I’m more experienced','Let me examine assumptions, signals and results.')}</fieldset>`;
  if(wizardStep===2) body=`<fieldset><legend>Your comfort with uncertainty</legend>${choice('risk','cautious','I prefer a steadier approach','Start with risk, bonds and smaller equity exposure.')}${choice('risk','balanced','I can accept some ups and downs','Show me a mix of different market exposures.')}${choice('risk','adventurous','I can accept larger swings','I want to understand equity-heavy approaches and their downside.')}</fieldset><fieldset><legend>When might you need the money?</legend><select name="horizon" aria-label="Time horizon"><option value="">Choose a time horizon</option><option value="short">Within 3 years</option><option value="medium">In 3–7 years</option><option value="long">In more than 7 years / learning only</option></select></fieldset><p class="small muted">These answers guide educational examples, not a personal investment recommendation.</p>`;
  $("wizard-content").innerHTML=`<p class="eyebrow">STEP ${wizardStep+1} OF 3</p><h2 id="step-title" tabindex="-1">${headings[wizardStep]}</h2>${body}`;
  if(wizardStep===2) $("journey-form").elements.horizon.value=draft.horizon;
  $("wizard-back").hidden=wizardStep===0;
  $("wizard-next").textContent=wizardStep===2?"Build my starting point →":"Continue →";
  $("step-title").focus({preventScroll:true});
}
function collectStep() {
  const form=new FormData($("journey-form"));
  if(wizardStep===0) {draft.goal=form.get('goal')||''; draft.topics=form.getAll('topics'); return !!draft.goal && draft.topics.length>0;}
  if(wizardStep===1) {draft.level=form.get('level')||''; return !!draft.level;}
  draft.risk=form.get('risk')||''; draft.horizon=form.get('horizon')||''; return !!draft.risk && !!draft.horizon;
}
$("journey-form").addEventListener("submit",e=>{
  e.preventDefault(); if(!collectStep()) {$("wizard-error").textContent="Please complete the choices above to continue.";$("wizard-error").hidden=false;return;}
  if(wizardStep<2) {wizardStep++;drawWizard();return;}
  journey={...draft,topics:[...draft.topics]};saveJourney();$("onboarding").hidden=true;$("workspace").hidden=false;
  renderJourney(); showPage("discover");
});
$("wizard-back").addEventListener("click",()=>{collectStep();wizardStep--;drawWizard();});
$("wizard-cancel").addEventListener("click",()=>{$("onboarding").hidden=true;$("workspace").hidden=false;showPage(currentPage);});
$("edit-journey").addEventListener("click",startWizard);

const PAGE_COPY={
  discover:["Find your next step.","A few thoughtful starting points, shaped around what you want to explore."],
  learn:["A little more understanding.","Read, save and explore. Every concept is a step toward a clearer decision."],
  strategies:["Different paths. Clear trade-offs.","Compare educational portfolio examples and understand the ideas behind them."],
  markets:["Get to know the markets.","Look beyond a price chart: understand what each asset represents and what moves it."],
  overview:["Turn an idea into an experiment.","Build a virtual portfolio and observe it through real historical prices."],
  history:["Keep the model honest.","Compare recorded expectations with what actually happened next."],
};
function showPage(name,focus=true) {
  if(!Object.hasOwn(PAGE_COPY,name)) name="discover";
  currentPage=name;
  for(const page of Object.keys(PAGE_COPY)) $(page).hidden=page!==name;
  document.querySelectorAll('[data-page]').forEach(b=>{b.classList.toggle('active',b.dataset.page===name);if(b.dataset.page===name)b.setAttribute('aria-current','page');else b.removeAttribute('aria-current');});
  $("page-title").textContent=PAGE_COPY[name][0];$("page-subtitle").textContent=PAGE_COPY[name][1];
  $("replay-bar").hidden=!["overview","history"].includes(name);$("methodology").hidden=!["overview","history","markets"].includes(name);
  if(focus) $("page-title").focus({preventScroll:true});
}
function preferredMix() {return journey.horizon==="short"?null:({cautious:"Conservative",balanced:"Balanced",adventurous:"Growth"})[journey.risk];}
function orderedLessons() {
  return [...LESSONS].sort((a,b)=>lessonScore(b)-lessonScore(a));
}
function lessonScore(l) {return (journey.topics.includes(l.topic)?6:0)+(l.level===journey.level?4:0)+(journey.level==="beginner"&&l.topic==="foundations"?8:0)+(journey.risk==="cautious"&&["risk","bonds"].includes(l.id)?3:0)+(journey.level==="advanced"&&l.id==="signals"?6:0);}
function lessonCard(l) {
  return `<article class="content-card"><div class="card-top"><span class="topic-label">${TOPICS[l.topic]}</span><button class="save-button" data-save="${l.id}" aria-pressed="${savedLessons.includes(l.id)}" aria-label="${savedLessons.includes(l.id)?'Unsave':'Save'} ${l.title}">${savedLessons.includes(l.id)?'★':'☆'}</button></div><span class="reading-meta">${LEVELS[l.level]} · ${l.minutes} min read</span><h3>${l.title}</h3><p>${l.description}</p><button class="text-button card-link" data-article="${l.id}">${completedLessons.includes(l.id)?'Read again ✓':'Read the guide →'}</button></article>`;
}
function weightsBar(weights) {return `<div class="allocation-bar" aria-hidden="true">${weights.map(w=>`<span style="width:${w}%"></span>`).join('')}</div><div class="allocation-labels">${weights.map((w,i)=>`<span>${['Equities','Bonds','Gold'][i]} <b>${w}%</b></span>`).join('')}</div>`;}
function mixCard(key) {
  const mix=MIXES[key], preferred=preferredMix()===key;
  return `<article class="content-card mix-card ${preferred?'suggested':''}"><div class="card-top"><span class="topic-label">${mix.tag}</span>${preferred?'<span class="pill">START HERE</span>':''}</div><h3>${mix.title}</h3><p>${mix.description}</p><div class="mix-allocation">${weightsBar(mix.weights)}</div><p class="tradeoff"><strong>Trade-off</strong> ${mix.tradeoff}</p>${preferred?`<p class="match-reason">Why this example? You chose “${RISKS[journey.risk]}”. These are fixed teaching weights, not a suitability assessment.</p>`:''}<div class="card-actions"><button class="secondary" data-mix="${key}">Explore in practice →</button><button class="text-button" data-article="buyhold">How it works</button></div></article>`;
}
function renderDiscover() {
  const next=orderedLessons().find(l=>!completedLessons.includes(l.id));
  const hero=journey.goal==='learn'?['Start with understanding.',next?`Your next guide: ${next.title}`:'You’ve read every guide. Revisit an idea or explore a portfolio.',next?`data-article="${next.id}"`:'data-go="learn"',next?'Continue learning →':'Browse the library →']:journey.goal==='explore'?['Curiosity is a good starting point.','Discover what stocks, bonds and gold represent before comparing their charts.','data-go="markets"','Explore the markets →']:['Give your ideas a practice run.','Understand an allocation, choose a virtual balance and observe what changes.','data-go="strategies"','Find a portfolio to explore →'];
  $("discover").innerHTML=`<div class="profile-strip"><span>${GOALS[journey.goal]}</span><span>${LEVELS[journey.level]}</span><span>${RISKS[journey.risk]}</span><span>${journey.topics.map(t=>TOPICS[t]).join(' · ')}</span></div><div class="discovery-hero"><div><p class="eyebrow">A STARTING POINT, NOT A FINISH LINE</p><h2>${hero[0]}</h2><p>${hero[1]}</p><button class="primary compact" ${hero[2]}>${hero[3]}</button></div><div class="learning-progress"><span class="progress-number">${completedLessons.length}<small> / ${LESSONS.length}</small></span><span>guides completed</span><div class="meter"><span style="width:${completedLessons.length/LESSONS.length*100}%"></span></div><button class="text-button" data-saved-library>${savedLessons.length} saved for later ↗</button></div></div><div class="section-heading"><div><p class="eyebrow">FOLLOW YOUR CURIOSITY</p><h2>${journey.level==='beginner'?'Build your foundations':'Go a little deeper'}</h2></div><button class="text-button" data-go="learn">Browse all guides →</button></div><p class="recommendation-note">Ordered by your interests and experience. ${journey.level==='beginner'?'Foundations come first so later ideas have context.':'You can open any guide, at any level.'}</p><div class="content-grid">${orderedLessons().slice(0,3).map(lessonCard).join('')}</div><div class="section-heading spaced"><div><p class="eyebrow">FROM UNDERSTANDING TO EXPLORING</p><h2>Find an approach to study</h2></div><button class="text-button" data-go="strategies">Compare every example →</button></div>${preferredMix()?`<div class="recommendation-layout">${mixCard(preferredMix())}<article class="panel next-step"><span class="step-number">↗</span><h3>Read the idea. Then test the mechanics.</h3><p>The replay lets you follow a fixed allocation through historical sessions. Watch its holdings and losses as well as its gains.</p><button class="text-button" data-article="buyhold">Understand buy-and-hold →</button><p class="small muted">No real money. No live trades.</p></article></div>`:'<div class="panel"><h3>Start with your time horizon.</h3><p class="muted">You may need the money within 3 years, so we have not highlighted a stock, bond or gold allocation for you. All three can lose value. Start by learning about risk; you can still compare every example as a virtual experiment.</p><button class="secondary" data-article="risk">Understand the trade-off →</button></div>'}`;
}
function renderLibrary() {
  const query=$("lesson-search").value.toLowerCase().trim(), topic=$("lesson-topic").value, saved=$("saved-only").checked;
  const lessons=orderedLessons().filter(l=>(topic==='all'||l.topic===topic)&&(!saved||savedLessons.includes(l.id))&&`${l.title} ${l.description} ${TOPICS[l.topic]} ${l.sections.flat().join(' ')}`.toLowerCase().includes(query));
  $("library-count").textContent=`${lessons.length} guide${lessons.length===1?'':'s'} · ${completedLessons.length} completed · ${savedLessons.length} saved`;
  $("lesson-grid").innerHTML=lessons.length?lessons.map(lessonCard).join(''):'<div class="panel empty-library"><h3>No guides match yet.</h3><p class="muted">Try another search, choose all topics or turn off “Saved only”.</p><button class="text-button" data-clear-filters>Clear filters →</button></div>';
}
function renderStrategies() {
  const keys=Object.keys(MIXES).sort((a,b)=>Number(b===preferredMix())-Number(a===preferredMix()));
  $("strategies").innerHTML=`<div class="section-heading"><h2>Three portfolios to explore</h2><span class="pill">EDUCATIONAL EXAMPLES</span></div><p class="recommendation-note">${preferredMix()?'Your stated risk preference determines which example appears first. Compare the trade-offs before trying one.':'Your short time horizon means no allocation is highlighted. You can still study each as a hypothetical example.'} Experience changes the reading path, not the portfolio weights.</p><div class="content-grid">${keys.map(mixCard).join('')}</div><div class="section-heading spaced"><div><p class="eyebrow">UNDERSTAND THE APPROACH</p><h2>A strategy is more than an allocation.</h2></div></div><div class="strategy-grid">${[
    ['buyhold','01','Buy & hold','Choose a mix, keep the units fixed and observe the result.','Available in practice'],
    ['dca','02','Regular contributions','Study investing equal amounts at regular intervals.','Learning guide · simulation not available'],
    ['rebalance','03','Rebalancing','Understand how an investor could respond to drifting weights.','Learning guide · simulation not available'],
    ['signals','04','Trend following','Examine momentum, false signals and the limits of accuracy.','Forecast inspection · no automated trading'],
  ].map(([id,n,title,copy,label])=>`<article class="content-card"><span class="strategy-number">${n}</span><h3>${title}</h3><p>${copy}</p><span class="reading-meta">${label}</span><button class="text-button card-link" data-article="${id}">Explore the approach →</button></article>`).join('')}</div>`;
}
function renderMarkets() {
  const info={SPY:['stocks','etfs','Own exposure to businesses','An equity fund gives exposure to company shares. Earnings expectations and market conditions can affect prices.'],IEF:['bonds','bonds','Understand government debt','A Treasury fund holds government bonds. Interest-rate changes can move its price; it is not a cash account.'],GLD:['gold','gold','Explore a physical asset through a trust','Gold exposure has a different structure from shares and bonds. It offers no guaranteed return or income.']};
  const ordered=Object.entries(info).sort((a,b)=>Number(journey.topics.includes(b[1][0]))-Number(journey.topics.includes(a[1][0])));
  $("markets").innerHTML=`<p class="context-note">Your interests come first. Prices follow the selected data mode above; replay is explicitly historical. Current quotes may be delayed.</p><div class="content-grid">${ordered.map(([symbol,[topic,lesson,title,copy]])=>{const signal=state?.signals.find(s=>s.symbol===symbol);return `<article class="content-card market-explainer"><span class="market-letter">${symbol}</span><span class="topic-label">${TOPICS[topic]}</span><h3>${title}</h3><p>${copy}</p>${signal?`<div class="explore-price">${money(signal.price)}<small>Close · ${dateLabel(state.date)}</small></div>${chart(signal.chart,'sparkline','#b5a0ff',`${symbol}: historical prices`)}`:'<p class="muted">Price data unavailable. You can still read the guide.</p>'}<button class="text-button card-link" data-article="${lesson}">Understand this market →</button></article>`;}).join('')}</div><div class="panel market-question"><h3>Not sure how these fit together?</h3><p class="muted">Start with diversification, then compare how different allocations change the balance of exposures.</p><button class="secondary" data-article="diversification">Connect the pieces →</button></div>`;
}
function renderJourney() { if(!journey)return;renderDiscover();renderLibrary();renderStrategies();renderMarkets(); }
function openArticle(id) {
  const l=LESSONS.find(l=>l.id===id);if(!l)return;
  const source=l.source?SOURCES[l.source]:null;
  $("reader-content").innerHTML=`<p class="eyebrow">${TOPICS[l.topic]} · ${l.minutes} MIN READ</p><h2 id="reader-title" tabindex="-1">${l.title}</h2><p class="reader-intro">${l.description}</p>${l.sections.map(([title,copy])=>`<section><h3>${title}</h3><p>${copy}</p></section>`).join('')}${source?`<div class="reader-source"><span class="reading-meta">KEEP READING · ORIGINAL SOURCE</span><a href="${source[1]}" target="_blank" rel="noopener noreferrer">${source[0]} ↗</a></div>`:'<p class="reader-source">Source: the MarketLens trained model, baselines and documented methodology.</p>'}<div class="reader-actions"><button class="primary compact" data-complete="${id}">${completedLessons.includes(id)?'Completed ✓':'Mark as read ✓'}</button><button class="secondary" data-save="${id}" aria-pressed="${savedLessons.includes(id)}">${savedLessons.includes(id)?'Saved ★':'Save for later ☆'}</button></div>${['buyhold','diversification'].includes(id)?'<button class="text-button card-link" data-go="strategies">Compare the portfolio examples →</button>':id==='signals'?'<button class="text-button card-link" data-go="history">Inspect model history →</button>':''}`;
  if(!$("reader").open)$("reader").showModal();
  $("reader-title").focus({preventScroll:true});$("reader").scrollTop=0;
}
$("close-reader").addEventListener("click",()=>$("reader").close());
$("reader").addEventListener("click",e=>{if(e.target===$("reader")){const r=$("reader").getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)$("reader").close();}});
function chooseMix(key) {
  if(!Object.hasOwn(MIXES,key))return;
  showPage('overview');
  if(state?.portfolio) $("practice-notice").textContent=`Your ${state.portfolio.profile} portfolio is already running. To try ${key}, reset the selected experiment first. Your holdings have not changed.`;
  else {$("profile").value=key;renderAllocation();$("practice-notice").textContent=`${MIXES[key].title} is selected. Review the weights, enter a virtual balance, then apply the allocation.`;}
  $("setup-heading").scrollIntoView({block:'center',behavior:'instant'});
}
document.addEventListener('click',e=>{
  const b=e.target.closest('button');if(!b)return;
  if(b.dataset.page)showPage(b.dataset.page);
  if(b.hasAttribute('data-saved-library')){$("lesson-search").value='';$("lesson-topic").value='all';$("saved-only").checked=true;renderLibrary();showPage('learn');}
  if(b.dataset.go){$("reader").close();showPage(b.dataset.go);}
  if(b.dataset.article)openArticle(b.dataset.article);
  if(b.dataset.mix)chooseMix(b.dataset.mix);
  if(b.dataset.save){const id=b.dataset.save;savedLessons=savedLessons.includes(id)?savedLessons.filter(x=>x!==id):[...savedLessons,id];saveJourney();renderJourney();if($("reader").open){b.textContent=savedLessons.includes(id)?'Saved ★':'Save for later ☆';b.setAttribute('aria-pressed',String(savedLessons.includes(id)));}}
  if(b.dataset.complete){const id=b.dataset.complete;if(!completedLessons.includes(id))completedLessons.push(id);saveJourney();renderJourney();b.textContent='Completed ✓';}
  if(b.hasAttribute('data-clear-filters')){$("lesson-search").value='';$("lesson-topic").value='all';$("saved-only").checked=false;renderLibrary();}
});
$("lesson-search").addEventListener('input',renderLibrary);$("lesson-topic").addEventListener('change',renderLibrary);$("saved-only").addEventListener('change',renderLibrary);
if(journey){$("workspace").hidden=false;renderJourney();showPage('discover',false);}else startWizard();
