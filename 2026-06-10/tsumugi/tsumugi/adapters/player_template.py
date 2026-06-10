"""同期プレビュープレイヤーの HTML テンプレート。

ChatGPT Codex 役のアダプタが生成する「完成形プレビュー」。
埋め込まれたマニフェスト(楽曲BPM・感情曲線・カット割り・色温度・
パレット)だけを入力として、ブラウザ内で音(WebAudio)と映像
(Canvas)をリアルタイム合成する。外部ファイル・外部通信なしで
動作する自己完結型。

演出方針: 感情曲線の変化が体感できること。
  - 音: arousal が低いと静かなパッドのみ、高いと4つ打ち+アルペジオ。
        valence で長調/短調、tension で不協和音が混ざる。
  - 映像: ショットごとに絵柄(光条/玉ボケ/粒子)とカメラが変わり、
        ビートに同期して明滅。場面転換時はラベルを大きく表示。

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
  .bar { flex: 1; height: 14px; background: #232043; border-radius: 7px; overflow: hidden; cursor: pointer; }
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
    <div class="bar" id="barBox"><div id="prog"></div></div>
    <div class="time" id="time">0.0 / 0.0</div>
  </div>
  <div class="meta" id="meta"></div>
  <div class="note">これはマニフェスト(BPM・感情曲線・カット割り・色温度)からブラウザ内で合成したシミュレーション試写です。
  実サービスのAPIを接続すると、この設計のまま本物の楽曲・映像に置き換わります。シークバーをクリックすると好きな位置から再生できます。</div>
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
document.getElementById("meta").innerHTML =
  "パレット: " + DATA.keyvisual.palette.map(c =>
    '<span class="sw" style="background:' + c + '"></span>').join("") +
  ' &nbsp;|&nbsp; 構成: ' + DATA.beats.map(b => b.label).join(" → ");

// ---- ユーティリティ ----
function moodAt(tn) {
  tn = Math.max(0, Math.min(1, tn));
  const bs = DATA.beats;
  if (tn <= bs[0].at) return bs[0].mood;
  for (let i = 0; i < bs.length - 1; i++) {
    const a = bs[i], b = bs[i + 1];
    if (tn <= b.at) {
      const t = (tn - a.at) / Math.max(1e-9, b.at - a.at);
      const lp = (x, y) => x + (y - x) * t;
      return { valence: lp(a.mood.valence, b.mood.valence),
               arousal: lp(a.mood.arousal, b.mood.arousal),
               tension: lp(a.mood.tension, b.mood.tension) };
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
  const sc = DATA.script.scenes || [];
  let cur = sc[0] || { text: "" };
  for (const s of sc) if (s.at <= tn) cur = s;
  return cur.text || "";
}
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
function mix(a, b, t) { return a.map((v, i) => Math.round(v + (b[i] - v) * t)); }
function hash(n) {
  let x = Math.sin(n * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
}
function hexRGB(hex) {
  const h = hex.replace("#", "");
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
}
// テーマ由来のパレット(TapNow役)とモチーフ(Seedance役)
const PALETTE = (DATA.keyvisual.palette || []).map(hexRGB);
const MOTIF_MODE = { rain: 1, snow: 0, particles: 0, bokeh: 2 }[DATA.video.motif];
function elementColor(col, i) {
  if (!PALETTE.length) return col;
  return mix(col, PALETTE[i % PALETTE.length], 0.55);
}

// ---- 音声合成(WebAudio)----
let ctx = null, master = null, padOscs = [], padGain = null, padFilter = null,
    tenOsc = null, tenGain = null, noiseBuf = null,
    startAt = 0, schedTimer = null, nextBeat = 0, beatIdx = 0;

const freq = m => 440 * Math.pow(2, (m - 69) / 12);
const ROOTS = [57, 53, 55, 50]; // A, F, G, D の進行(1小節ごと)

function initAudio() {
  ctx = new (window.AudioContext || window.webkitAudioContext)();
  master = ctx.createGain(); master.gain.value = 0.85; master.connect(ctx.destination);
  noiseBuf = ctx.createBuffer(1, ctx.sampleRate * 0.1, ctx.sampleRate);
  const d = noiseBuf.getChannelData(0);
  for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
  padFilter = ctx.createBiquadFilter(); padFilter.type = "lowpass"; padFilter.frequency.value = 600;
  padGain = ctx.createGain(); padGain.gain.value = 0;
  padFilter.connect(padGain); padGain.connect(master);
  padOscs = [0, 1, 2].map(() => {
    const o = ctx.createOscillator(); o.type = "sawtooth";
    o.detune.value = (Math.random() - 0.5) * 14;
    o.connect(padFilter); o.start(); return o;
  });
  tenOsc = ctx.createOscillator(); tenOsc.type = "sine";
  tenGain = ctx.createGain(); tenGain.gain.value = 0;
  tenOsc.connect(tenGain); tenGain.connect(master); tenOsc.start();
}
function chordTones(bar, m) {
  const root = ROOTS[bar % ROOTS.length];
  const third = m.valence >= 0 ? 4 : 3; // 長調/短調
  return [root, root + third, root + 7, root + 12];
}
function setChord(t, bar, m) {
  const tones = chordTones(bar, m);
  tones.slice(0, 3).forEach((n, i) =>
    padOscs[i].frequency.setTargetAtTime(freq(n), t, 0.06));
  tenOsc.frequency.setTargetAtTime(freq(tones[0] + 13), t, 0.06); // 短9度=緊張
}
function thump(t, f0, f1, dur, gain) {
  const o = ctx.createOscillator(), g = ctx.createGain();
  o.frequency.setValueAtTime(f0, t);
  o.frequency.exponentialRampToValueAtTime(Math.max(1, f1), t + dur);
  g.gain.setValueAtTime(gain, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + dur);
  o.connect(g); g.connect(master); o.start(t); o.stop(t + dur + 0.02);
}
function hat(t, gain) {
  const s = ctx.createBufferSource(); s.buffer = noiseBuf;
  const f = ctx.createBiquadFilter(); f.type = "highpass"; f.frequency.value = 6500;
  const g = ctx.createGain();
  g.gain.setValueAtTime(gain, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + 0.05);
  s.connect(f); f.connect(g); g.connect(master); s.start(t);
}
function snare(t, gain) {
  const s = ctx.createBufferSource(); s.buffer = noiseBuf;
  const f = ctx.createBiquadFilter(); f.type = "bandpass"; f.frequency.value = 1800;
  const g = ctx.createGain();
  g.gain.setValueAtTime(gain, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + 0.12);
  s.connect(f); f.connect(g); g.connect(master); s.start(t);
}
function pluck(t, f, gain) {
  const o = ctx.createOscillator(); o.type = "triangle";
  const g = ctx.createGain();
  o.frequency.value = f;
  g.gain.setValueAtTime(gain, t);
  g.gain.exponentialRampToValueAtTime(0.001, t + 0.18);
  o.connect(g); g.connect(master); o.start(t); o.stop(t + 0.2);
}
function scheduleBeat(t, i) {
  const tn = (t - startAt) / DUR;
  if (tn > 1) return;
  const m = moodAt(tn);
  const bar = Math.floor(i / 4);
  const tones = chordTones(bar, m);
  if (i % 4 === 0) setChord(t, bar, m);

  // ドラム: 静→4拍に1回 / 動→4つ打ち+スネア+裏ハイハット
  if (m.arousal > 0.6) thump(t, 130, 44, 0.22, 0.16 + 0.28 * m.arousal);
  else if (i % 4 === 0) thump(t, 120, 46, 0.28, 0.08 + 0.2 * m.arousal);
  if (i % 4 === 2 && m.arousal > 0.4) snare(t, 0.05 + 0.12 * m.arousal);
  if (m.arousal > 0.15) hat(t, 0.012 + 0.05 * m.arousal);
  if (m.arousal > 0.5) hat(t + BEAT / 2, 0.01 + 0.035 * m.arousal);

  // ベース
  pluck(t, freq(tones[0] - 24), 0.05 + 0.12 * m.arousal);

  // アルペジオ: 盛り上がるほど細かく(8分→16分)
  if (m.arousal > 0.3) {
    const sub = m.arousal > 0.6 ? 4 : 2;
    for (let k = 0; k < sub; k++) {
      const tone = tones[(i * sub + k) % tones.length] + 12 + (m.valence > 0.4 ? 12 : 0);
      pluck(t + (k * BEAT) / sub, freq(tone), 0.02 + 0.07 * m.arousal);
    }
  }

  // 連続パラメータ
  padFilter.frequency.setTargetAtTime(220 + m.arousal * 4200, t, 0.2);
  padGain.gain.setTargetAtTime(0.02 + 0.11 * m.arousal, t, 0.25);
  tenGain.gain.setTargetAtTime(m.tension * 0.022, t, 0.25);
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
let lastLabel = null, labelT = -10;
const WARM = [255, 168, 110], COOL = [105, 155, 255];

function draw(el) {
  const tn = Math.max(0, Math.min(1, el / DUR));
  const m = moodAt(tn);
  // 基調色 = 色温度 × valence の色味(陽=暖色 / 陰=寒色)
  const base = kelvinRGB(kelvinAt(tn));
  const col = mix(base, m.valence >= 0 ? WARM : COOL, Math.min(0.6, Math.abs(m.valence) * 0.7));
  const shot = Math.floor(el / CUT);
  const sh = hash(shot);
  // 絵柄: テーマのモチーフを主(7割)としつつ、ショットごとに変化させる
  const mode = (MOTIF_MODE !== undefined && hash(shot + 57) < 0.7)
    ? MOTIF_MODE : Math.floor(hash(shot + 31) * 3);
  const beatPhase = (el % BEAT) / BEAT;
  const pulse = Math.pow(1 - beatPhase, 2) * m.arousal; // 拍頭で明滅

  // カメラ(ショットごとにズーム・パンが変わる)
  const zoom = 1.04 + 0.05 * sh + 0.025 * pulse;
  const panx = (sh - 0.5) * 60 + Math.sin(el * 0.3 + shot) * 12;
  const pany = (hash(shot + 5) - 0.5) * 40;
  g2.save();
  g2.translate(W / 2 + panx, H / 2 + pany);
  g2.scale(zoom, zoom);
  g2.translate(-W / 2, -H / 2);

  // 背景グラデーション
  const grad = sh < 0.5
    ? g2.createLinearGradient(0, 0, W, H) : g2.createLinearGradient(W, 0, 0, H);
  const dim = 0.10 + 0.10 * m.arousal + 0.08 * pulse;
  grad.addColorStop(0, "rgb(" + (col[0] * dim | 0) + "," + (col[1] * dim | 0) + "," + (col[2] * dim * 1.3 | 0) + ")");
  grad.addColorStop(1, "rgb(" + (col[0] * (dim + 0.32) | 0) + "," + (col[1] * (dim + 0.26) | 0) + "," + (col[2] * (dim + 0.34) | 0) + ")");
  g2.fillStyle = grad; g2.fillRect(-80, -80, W + 160, H + 160);

  // 光源(拍に同期して脈動)
  const cx = W * (0.25 + 0.5 * hash(shot + 7)), cy = H * (0.25 + 0.4 * hash(shot + 13));
  const glow = g2.createRadialGradient(cx, cy, 0, cx, cy, H * (0.5 + 0.3 * pulse + 0.2 * m.arousal));
  glow.addColorStop(0, "rgba(" + col[0] + "," + col[1] + "," + col[2] + "," + (0.12 + 0.3 * m.arousal + 0.2 * pulse) + ")");
  glow.addColorStop(1, "rgba(0,0,0,0)");
  g2.fillStyle = glow; g2.fillRect(-80, -80, W + 160, H + 160);

  const rgba = (c, a) => "rgba(" + c[0] + "," + c[1] + "," + c[2] + "," + a + ")";
  if (mode === 0) {
    // 粒子ドリフト(snow モチーフ時はゆっくり降下する)
    const falling = DATA.video.motif === "snow";
    const n = Math.floor(30 + 100 * m.arousal);
    for (let i = 0; i < n; i++) {
      const sp = 25 + 110 * m.arousal;
      let px, py;
      if (falling) {
        px = hash(i * 3 + 1) * W + Math.sin(el * (1 + m.tension) + i) * 18;
        py = ((hash(i * 7 + 2) * H + el * (20 + 50 * m.arousal) * (0.5 + hash(i))) % (H + 40)) - 20;
      } else {
        px = ((hash(i * 3 + 1) * W + el * sp * (0.4 + hash(i))) % (W + 40)) - 20;
        const jy = Math.sin(el * (2 + 7 * m.tension) + i * 2.4) * (4 + 30 * m.tension);
        py = hash(i * 7 + 2) * H + jy;
      }
      g2.fillStyle = rgba(elementColor(col, i), 0.2 + 0.4 * hash(i * 5));
      g2.beginPath(); g2.arc(px, py, 1 + 3.4 * hash(i * 11 + 3), 0, 7); g2.fill();
    }
  } else if (mode === 1) {
    // 雨の光条
    const n = Math.floor(40 + 110 * m.arousal);
    for (let i = 0; i < n; i++) {
      const sx = hash(i * 13 + shot) * W + Math.sin(el + i) * 6 * m.tension;
      const speed = 280 + 600 * m.arousal;
      const sy = ((hash(i * 17) * H + el * speed * (0.5 + 0.7 * hash(i + shot))) % (H + 200)) - 120;
      const len = 30 + 150 * m.arousal;
      g2.strokeStyle = rgba(elementColor(col, i), 0.1 + 0.3 * hash(i * 3));
      g2.lineWidth = 1 + 1.6 * hash(i * 9);
      g2.beginPath(); g2.moveTo(sx, sy); g2.lineTo(sx + 6 * m.tension, sy + len); g2.stroke();
    }
  } else {
    // 玉ボケ
    const n = Math.floor(14 + 26 * m.arousal);
    for (let i = 0; i < n; i++) {
      const dir = hash(i * 19) > 0.5 ? 1 : -1;
      const bx = ((hash(i * 23 + shot) * W + el * dir * (12 + 45 * m.arousal)) % (W + 240) + W + 240) % (W + 240) - 120;
      const by = hash(i * 29) * H + Math.sin(el * 0.7 + i) * 22 * m.tension;
      const r = 18 + 85 * hash(i * 31 + shot);
      g2.fillStyle = rgba(elementColor(col, i), 0.05 + 0.13 * hash(i * 7) + 0.05 * pulse);
      g2.beginPath(); g2.arc(bx, by, r, 0, 7); g2.fill();
    }
  }
  g2.restore();

  // カット瞬間のフラッシュ
  const since = el % CUT;
  if (since < 0.1) {
    g2.fillStyle = "rgba(255,255,255," + (0.22 * (1 - since / 0.1) * (0.35 + 0.65 * m.arousal)) + ")";
    g2.fillRect(0, 0, W, H);
  }

  // 場面転換: ラベルを大きく表示
  const beat = beatInfoAt(tn);
  if (beat.label !== lastLabel) { lastLabel = beat.label; labelT = el; }
  const dt = el - labelT;
  if (dt < 1.5) {
    const a = 1 - dt / 1.5;
    g2.fillStyle = "rgba(0,0,0," + 0.35 * a + ")"; g2.fillRect(0, 0, W, H);
    g2.fillStyle = "rgba(232,230,245," + a + ")";
    g2.font = "700 " + Math.round(90 + 50 * dt) + "px serif";
    g2.textAlign = "center";
    g2.fillText(beat.label, W / 2, H / 2 + 30);
    g2.textAlign = "left";
  }

  // レターボックス + テキスト
  g2.fillStyle = "rgba(0,0,0,0.82)";
  g2.fillRect(0, 0, W, 54); g2.fillRect(0, H - 96, W, 96);
  g2.fillStyle = "#e8e6f5"; g2.font = "26px sans-serif";
  g2.fillText("【" + beat.label + "】", 28, H - 56);
  g2.font = "20px sans-serif"; g2.fillStyle = "#bdb8e0";
  g2.fillText(sceneTextAt(tn).slice(0, 52), 110, H - 56);
  g2.font = "15px sans-serif"; g2.fillStyle = "#9b96c2";
  g2.fillText(DATA.title + " — shot " + (shot + 1) + " · " + Math.round(kelvinAt(tn)) + "K", 28, 34);
  const meters = [["V", (m.valence + 1) / 2, "#c084fc"], ["A", m.arousal, "#5eead4"], ["T", m.tension, "#fbbf24"]];
  meters.forEach(([label, v, c], i) => {
    const x = W - 220 + i * 70;
    g2.fillStyle = "#9b96c2"; g2.font = "13px sans-serif"; g2.fillText(label, x, 34);
    g2.fillStyle = "#353060"; g2.fillRect(x + 14, 24, 44, 8);
    g2.fillStyle = c; g2.fillRect(x + 14, 24, 44 * v, 8);
  });
}

// ---- 再生制御 ----
const btnPlay = document.getElementById("play"), btnRestart = document.getElementById("restart");
const prog = document.getElementById("prog"), timeEl = document.getElementById("time");
const barBox = document.getElementById("barBox");
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
async function startFrom(sec) {
  stopAll();
  ended = false;
  initAudio();
  await ctx.resume();
  startAt = ctx.currentTime + 0.08 - sec;
  beatIdx = Math.ceil(sec / BEAT);
  nextBeat = startAt + beatIdx * BEAT;
  startScheduler(); loop();
  btnPlay.textContent = "⏸ 一時停止";
}
btnPlay.onclick = async () => {
  if (!ctx) { await startFrom(0); }
  else if (ctx.state === "running") {
    await ctx.suspend(); cancelAnimationFrame(raf);
    btnPlay.textContent = "▶ 再生";
  } else {
    await ctx.resume(); loop();
    btnPlay.textContent = "⏸ 一時停止";
  }
};
btnRestart.onclick = () => startFrom(0);
barBox.onclick = (e) => {
  const rect = barBox.getBoundingClientRect();
  const sec = Math.max(0, Math.min(0.999, (e.clientX - rect.left) / rect.width)) * DUR;
  startFrom(sec);
};
draw(0);
timeEl.textContent = "0.0 / " + DUR.toFixed(1);
</script>
</body>
</html>
"""
