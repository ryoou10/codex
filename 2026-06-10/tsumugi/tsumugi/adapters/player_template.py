"""同期プレビュープレイヤーの HTML テンプレート。

ChatGPT Codex 役のアダプタが生成する「完成形プレビュー」。
埋め込まれたマニフェスト(楽曲BPM・感情曲線・カット割り・色温度・
パレット)だけを入力として、ブラウザ内で音(WebAudio)と映像
(Canvas)をリアルタイム合成する。外部ファイル・外部通信なしで
動作する自己完結型。

プレースホルダ:
    __TITLE__      作品題名(HTMLエスケープ済みで渡すこと)
    __DATA_JSON__  全マニフェストの JSON("</" はエスケープ済みで渡すこと)
"""

PLAYER_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ - TSUMUGI preview</title>
<style>
  body { margin: 0; background: #0c0a14; color: #e8e6f5; font-family: "Hiragino Sans", "Noto Sans JP", sans-serif; }
  .wrap { max-width: 880px; margin: 0 auto; padding: 18px; }
  h1 { font-size: 18px; margin: 0 0 2px; }
  .sub { color: #9b96c2; font-size: 12px; margin-bottom: 12px; }
  canvas { width: 100%; border-radius: 10px; display: block; background: #000; }
  .controls { display: flex; gap: 10px; align-items: center; margin-top: 12px; }
  button { background: #c084fc; border: none; color: #1b1030; font-weight: 700; font-size: 14px;
           border-radius: 8px; padding: 9px 18px; cursor: pointer; }
  button.ghost { background: #232043; color: #e8e6f5; border: 1px solid #353060; }
  .bar { flex: 1; height: 8px; background: #232043; border-radius: 4px; overflow: hidden; }
  .bar > div { height: 100%; width: 0; background: linear-gradient(90deg, #c084fc, #5eead4); }
  .time { font-variant-numeric: tabular-nums; font-size: 13px; color: #9b96c2; min-width: 86px; text-align: right; }
  .meta { display: flex; gap: 14px; margin-top: 10px; font-size: 12px; color: #9b96c2; flex-wrap: wrap; }
  .sw { display: inline-block; width: 14px; height: 14px; border-radius: 3px; vertical-align: -2px; margin-right: 3px; }
  .note { margin-top: 12px; font-size: 11px; color: #6b668f; }
</style>
</head>
<body>
<div class="wrap">
  <h1>__TITLE__</h1>
  <div class="sub" id="sub"></div>
  <canvas id="cv" width="1280" height="720"></canvas>
  <div class="controls">
    <button id="play">▶ 再生</button>
    <button id="restart" class="ghost">⟲ 最初から</button>
    <div class="bar"><div id="prog"></div></div>
    <div class="time" id="time">0.0 / 0.0</div>
  </div>
  <div class="meta" id="meta"></div>
  <div class="note">これはマニフェスト(BPM・感情曲線・カット割り・色温度)からブラウザ内で合成したシミュレーションプレビューです。
  実サービスのAPIを接続すると、この設計のまま本物の楽曲・映像に置き換わります。</div>
</div>
<script id="data" type="application/json">__DATA_JSON__</script>
<script>
"use strict";
const DATA = JSON.parse(document.getElementById("data").textContent);
const DUR = DATA.duration_sec;
const BPM = DATA.music.bpm;
const BEAT = 60 / BPM;
const CUT = 60 / DATA.video.cuts_per_min;

document.getElementById("sub").textContent =
  DATA.theme + " — " + Math.round(DUR) + "s · " + BPM + " BPM · " +
  DATA.video.cuts_per_min + " cuts/min";
const meta = document.getElementById("meta");
meta.innerHTML = "パレット: " + DATA.keyvisual.palette.map(c =>
  '<span class="sw" style="background:' + c + '"></span>').join("") +
  ' &nbsp;|&nbsp; 構成: ' + DATA.beats.map(b => b.label).join(" → ");

// ---- 感情曲線(ビート間を線形補間)----
function moodAt(tn) {
  tn = Math.max(0, Math.min(1, tn));
  const bs = DATA.beats;
  if (tn <= bs[0].at) return bs[0].mood;
  for (let i = 0; i < bs.length - 1; i++) {
    const a = bs[i], b = bs[i + 1];
    if (tn <= b.at) {
      const t = (tn - a.at) / Math.max(1e-9, b.at - a.at);
      const lerp = (x, y) => x + (y - x) * t;
      return { valence: lerp(a.mood.valence, b.mood.valence),
               arousal: lerp(a.mood.arousal, b.mood.arousal),
               tension: lerp(a.mood.tension, b.mood.tension) };
    }
  }
  return bs[bs.length - 1].mood;
}
function beatInfoAt(tn) {
  let cur = DATA.beats[0];
  for (const b of DATA.beats) if (b.at <= tn) cur = b;
  return cur;
}
function sceneTextAt(tn) {
  let cur = DATA.script.scenes[0];
  for (const s of DATA.script.scenes) if (s.at <= tn) cur = s;
  return cur.text;
}
// 映像マニフェストの色温度を補間
function kelvinAt(tn) {
  const sc = DATA.video.scenes;
  if (tn <= sc[0].at) return sc[0].color_temp_k;
  for (let i = 0; i < sc.length - 1; i++) {
    const a = sc[i], b = sc[i + 1];
    if (tn <= b.at) {
      const t = (tn - a.at) / Math.max(1e-9, b.at - a.at);
      return a.color_temp_k + (b.color_temp_k - a.color_temp_k) * t;
    }
  }
  return sc[sc.length - 1].color_temp_k;
}
function kelvinRGB(k) { // Tanner Helland 近似
  k /= 100;
  let r = k <= 66 ? 255 : 329.7 * Math.pow(k - 60, -0.1332);
  let g = k <= 66 ? 99.47 * Math.log(k) - 161.1 : 288.1 * Math.pow(k - 60, -0.0755);
  let b = k >= 66 ? 255 : (k <= 19 ? 0 : 138.5 * Math.log(k - 10) - 305.0);
  const cl = v => Math.max(0, Math.min(255, Math.round(v)));
  return [cl(r), cl(g), cl(b)];
}
function hash(n) { // 決定論的擬似乱数 [0,1)
  let x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
}

// ---- 音声合成(WebAudio)----
let ctx = null, master = null, padOscs = [], padGain = null, padFilter = null,
    tenOsc = null, tenGain = null, noiseBuf = null,
    startAt = 0, schedTimer = null, nextBeat = 0, beatIdx = 0, chordIdx = 0;

const freq = m => 440 * Math.pow(2, (m - 69) / 12);
const ROOTS = [57, 53, 55, 50]; // A, F, G, D の進行

function initAudio() {
  ctx = new (window.AudioContext || window.webkitAudioContext)();
  master = ctx.createGain(); master.gain.value = 0.8; master.connect(ctx.destination);
  noiseBuf = ctx.createBuffer(1, ctx.sampleRate * 0.1, ctx.sampleRate);
  const d = noiseBuf.getChannelData(0);
  for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
  padFilter = ctx.createBiquadFilter(); padFilter.type = "lowpass"; padFilter.frequency.value = 800;
  padGain = ctx.createGain(); padGain.gain.value = 0;
  padFilter.connect(padGain); padGain.connect(master);
  padOscs = [0, 1, 2].map(() => {
    const o = ctx.createOscillator(); o.type = "sawtooth";
    o.detune.value = (Math.random() - 0.5) * 12;
    o.connect(padFilter); o.start(); return o;
  });
  tenOsc = ctx.createOscillator(); tenOsc.type = "sine";
  tenGain = ctx.createGain(); tenGain.gain.value = 0;
  tenOsc.connect(tenGain); tenGain.connect(master); tenOsc.start();
}
function setChord(t, m) {
  const root = ROOTS[chordIdx % ROOTS.length];
  const third = m.valence >= 0 ? 4 : 3; // 長調/短調
  [root, root + third, root + 7].forEach((n, i) =>
    padOscs[i].frequency.setTargetAtTime(freq(n), t, 0.08));
  tenOsc.frequency.setTargetAtTime(freq(root + 13), t, 0.08); // 短9度=緊張
  chordIdx++;
}
function thump(t, f0, f1, dur, gain) {
  const o = ctx.createOscillator(), g = ctx.createGain();
  o.frequency.setValueAtTime(f0, t);
  o.frequency.exponentialRampToValueAtTime(f1, t + dur);
  g.gain.setValueAtTime(gain, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + dur);
  o.connect(g); g.connect(master); o.start(t); o.stop(t + dur + 0.02);
}
function hat(t, gain) {
  const s = ctx.createBufferSource(); s.buffer = noiseBuf;
  const f = ctx.createBiquadFilter(); f.type = "highpass"; f.frequency.value = 6000;
  const g = ctx.createGain();
  g.gain.setValueAtTime(gain, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + 0.05);
  s.connect(f); f.connect(g); g.connect(master); s.start(t);
}
function scheduleBeat(t, i) {
  const tn = (t - startAt) / DUR;
  if (tn > 1) return;
  const m = moodAt(tn);
  if (i % 8 === 0) setChord(t, m);
  if (i % 4 === 0) thump(t, 130, 45, 0.25, 0.12 + 0.3 * m.arousal);          // キック
  if (i % 2 === 1 && m.arousal > 0.45) thump(t, 220, 180, 0.12, 0.05 * m.arousal); // スネア風
  if (m.arousal > 0.2) hat(t, 0.015 + 0.05 * m.arousal);
  const root = ROOTS[Math.floor(i / 8) % ROOTS.length];
  if (i % 2 === 0) thump(t, freq(root - 12), freq(root - 12), 0.3, 0.05 + 0.08 * m.arousal); // ベース
  padFilter.frequency.setTargetAtTime(250 + m.arousal * 3800, t, 0.25);
  padGain.gain.setTargetAtTime(0.035 + 0.085 * m.arousal, t, 0.3);
  tenGain.gain.setTargetAtTime(m.tension * 0.02, t, 0.3);
}
function startScheduler() {
  schedTimer = setInterval(() => {
    while (nextBeat < ctx.currentTime + 0.15) {
      scheduleBeat(nextBeat, beatIdx);
      nextBeat += BEAT; beatIdx++;
    }
  }, 50);
}

// ---- 映像合成(Canvas)----
const cv = document.getElementById("cv"), g2 = cv.getContext("2d");
const W = cv.width, H = cv.height;
function draw(el) {
  const tn = Math.max(0, Math.min(1, el / DUR));
  const m = moodAt(tn);
  const [r, gc, b] = kelvinRGB(kelvinAt(tn));
  const shot = Math.floor(el / CUT);
  const sh = hash(shot);

  // 背景グラデーション(色温度ベース、ショットごとに向きが変わる)
  const grad = sh < 0.5
    ? g2.createLinearGradient(0, 0, W, H) : g2.createLinearGradient(W, 0, 0, H);
  grad.addColorStop(0, "rgb(" + (r * 0.16 | 0) + "," + (gc * 0.16 | 0) + "," + (b * 0.22 | 0) + ")");
  grad.addColorStop(1, "rgb(" + (r * 0.5 | 0) + "," + (gc * 0.42 | 0) + "," + (b * 0.5 | 0) + ")");
  g2.fillStyle = grad; g2.fillRect(0, 0, W, H);

  // 光源(arousal で強く)
  const cx = W * (0.25 + 0.5 * hash(shot + 7)), cy = H * (0.25 + 0.4 * hash(shot + 13));
  const glow = g2.createRadialGradient(cx, cy, 0, cx, cy, H * 0.8);
  glow.addColorStop(0, "rgba(" + r + "," + gc + "," + b + "," + (0.10 + 0.30 * m.arousal) + ")");
  glow.addColorStop(1, "rgba(0,0,0,0)");
  g2.fillStyle = glow; g2.fillRect(0, 0, W, H);

  // パーティクル(数=arousal、揺れ=tension)
  const n = Math.floor(25 + 95 * m.arousal);
  for (let i = 0; i < n; i++) {
    const sp = 18 + 90 * m.arousal;
    const px = ((hash(i * 3 + 1) * W + el * sp * (0.4 + hash(i)) ) % (W + 40)) - 20;
    const jy = Math.sin(el * (2 + 6 * m.tension) + i * 2.4) * (4 + 26 * m.tension);
    const py = hash(i * 7 + 2) * H + jy;
    const sz = 1 + 3.2 * hash(i * 11 + 3);
    g2.fillStyle = "rgba(" + r + "," + gc + "," + b + "," + (0.18 + 0.4 * hash(i * 5)) + ")";
    g2.beginPath(); g2.arc(px, py, sz, 0, 7); g2.fill();
  }

  // カット瞬間のフラッシュ + レターボックス
  const since = el % CUT;
  if (since < 0.12) {
    g2.fillStyle = "rgba(255,255,255," + (0.20 * (1 - since / 0.12) * (0.4 + 0.6 * m.arousal)) + ")";
    g2.fillRect(0, 0, W, H);
  }
  g2.fillStyle = "rgba(0,0,0,0.82)";
  g2.fillRect(0, 0, W, 54); g2.fillRect(0, H - 96, W, 96);

  // テキスト(現在のビートと脚本)
  const beat = beatInfoAt(tn);
  g2.fillStyle = "#e8e6f5"; g2.font = "26px sans-serif"; g2.textAlign = "left";
  g2.fillText("【" + beat.label + "】", 28, H - 56);
  g2.font = "20px sans-serif"; g2.fillStyle = "#bdb8e0";
  g2.fillText(sceneTextAt(tn).slice(0, 52), 110, H - 56);
  g2.font = "15px sans-serif"; g2.fillStyle = "#9b96c2";
  g2.fillText(DATA.title + " — shot " + (shot + 1) + " · " + Math.round(kelvinAt(tn)) + "K", 28, 34);
  // 感情メーター
  const meters = [["V", (m.valence + 1) / 2, "#c084fc"], ["A", m.arousal, "#5eead4"], ["T", m.tension, "#fbbf24"]];
  meters.forEach(([label, v, col], i) => {
    const x = W - 220 + i * 70;
    g2.fillStyle = "#9b96c2"; g2.font = "13px sans-serif"; g2.fillText(label, x, 34);
    g2.fillStyle = "#353060"; g2.fillRect(x + 14, 24, 44, 8);
    g2.fillStyle = col; g2.fillRect(x + 14, 24, 44 * v, 8);
  });
}

// ---- 再生制御 ----
const btnPlay = document.getElementById("play"), btnRestart = document.getElementById("restart");
const prog = document.getElementById("prog"), timeEl = document.getElementById("time");
let raf = null, ended = false;

function elapsed() { return ctx ? Math.max(0, ctx.currentTime - startAt) : 0; }
function loop() {
  const el = Math.min(elapsed(), DUR);
  draw(el);
  prog.style.width = (el / DUR * 100) + "%";
  timeEl.textContent = el.toFixed(1) + " / " + DUR.toFixed(1);
  if (el >= DUR && !ended) { ended = true; stopAll(); btnPlay.textContent = "▶ 再生"; return; }
  raf = requestAnimationFrame(loop);
}
function stopAll() {
  if (schedTimer) clearInterval(schedTimer);
  if (ctx) { ctx.close(); ctx = null; }
  if (raf) cancelAnimationFrame(raf);
}
btnPlay.onclick = async () => {
  if (!ctx) { // 最初から再生
    ended = false; beatIdx = 0; chordIdx = 0;
    initAudio();
    await ctx.resume();
    startAt = ctx.currentTime + 0.1; nextBeat = startAt;
    startScheduler(); loop();
    btnPlay.textContent = "⏸ 一時停止";
  } else if (ctx.state === "running") {
    await ctx.suspend(); cancelAnimationFrame(raf);
    btnPlay.textContent = "▶ 再生";
  } else {
    await ctx.resume(); loop();
    btnPlay.textContent = "⏸ 一時停止";
  }
};
btnRestart.onclick = () => { stopAll(); btnPlay.textContent = "▶ 再生"; prog.style.width = "0"; draw(0); };
draw(0);
timeEl.textContent = "0.0 / " + DUR.toFixed(1);
</script>
</body>
</html>
"""
