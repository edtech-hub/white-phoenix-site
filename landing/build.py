#!/usr/bin/env python3
"""
Niche landing-page generator.

Reads each landing/niches/<slug>.json config, injects the per-niche demo
partial (landing/niches/<slug>.demo.html), and writes a standalone static
page to lp/<slug>.html — ready to deploy on GitHub Pages and send in a
campaign. Each page is fully static (unique <title>/description/OG tags) so
SMS and link previews render correctly without running JavaScript.

Usage:
    python3 landing/build.py            # build every niche
    python3 landing/build.py event-planners   # build one niche
"""

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent          # landing/
REPO = ROOT.parent                              # repo root
NICHES = ROOT / "niches"
OUT = REPO / "lp"


def esc(s):
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- CSS (shared)
CSS = r"""
:root{
  --porcelain:#FBFAF8;--paper:#FFFFFF;--ink:#16181D;--ink-soft:#3A3E47;--ash:#7C818B;
  --line:#E8E6E1;--flame:#FF5C1A;--flame-deep:#E8430A;--ember:#FFB42E;
  --night:#0E1014;--night-soft:#171A20;--night-line:rgba(255,255,255,.09);
  --grad:linear-gradient(92deg,#FF5C1A 0%,#FFB42E 100%);
  --display:'Clash Display',sans-serif;--body:'Inter',sans-serif;
  --radius:18px;--shadow:0 18px 50px -22px rgba(22,24,29,.22);--maxw:1180px;
}
*{margin:0;padding:0;box-sizing:border-box}
html{scroll-behavior:smooth}
body{font-family:var(--body);background:var(--porcelain);color:var(--ink);line-height:1.6;-webkit-font-smoothing:antialiased;overflow-x:hidden}
img,svg{display:block}
a{color:inherit;text-decoration:none}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 24px}
h1,h2,h3,.display{font-family:var(--display);font-weight:600;line-height:1.08;letter-spacing:-.015em}
h2{font-size:clamp(2rem,4vw,3.1rem)}
h3{font-size:1.32rem;line-height:1.25}
p{color:var(--ink-soft)}
.eyebrow{display:inline-flex;align-items:center;gap:.55rem;font-size:.78rem;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:var(--flame-deep)}
.eyebrow::before{content:"";width:22px;height:2px;background:var(--grad);border-radius:2px}
section{padding:104px 0}
@media(max-width:760px){section{padding:72px 0}}
.ember-line{position:relative;display:inline-block}
.ember-line::after{content:"";position:absolute;left:0;bottom:-.14em;width:100%;height:.09em;background:var(--grad);border-radius:99px;transform:scaleX(0);transform-origin:left;transition:transform .9s cubic-bezier(.2,.7,.2,1) .25s}
.in-view .ember-line::after{transform:scaleX(1)}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:.55rem;font-family:var(--body);font-weight:600;font-size:.98rem;padding:.95rem 1.7rem;border-radius:99px;border:1px solid transparent;cursor:pointer;transition:transform .2s ease,box-shadow .2s ease,background .2s ease,color .2s ease;white-space:nowrap}
.btn-flame{background:var(--grad);color:#fff;box-shadow:0 12px 28px -12px rgba(232,67,10,.55)}
.btn-flame:hover{transform:translateY(-2px);box-shadow:0 16px 34px -12px rgba(232,67,10,.65)}
.btn-ghost{background:transparent;color:var(--ink);border-color:#CFCBC3}
.btn-ghost:hover{border-color:var(--ink);transform:translateY(-2px)}
.btn:focus-visible{outline:3px solid var(--ember);outline-offset:3px}
a:focus-visible{outline:3px solid var(--ember);outline-offset:3px;border-radius:6px}
/* Nav */
header{position:fixed;top:0;left:0;right:0;z-index:100;transition:background .25s ease,box-shadow .25s ease,border-color .25s ease;background:rgba(251,250,248,.82);backdrop-filter:blur(14px);border-bottom:1px solid var(--line)}
header.scrolled{background:rgba(251,250,248,.94);box-shadow:0 8px 30px -16px rgba(22,24,29,.18)}
.nav{display:flex;align-items:center;justify-content:space-between;height:74px}
.logo{display:flex;align-items:center;gap:.6rem;font-family:var(--display);font-weight:600;font-size:1.18rem;letter-spacing:-.01em}
.logo svg{width:30px;height:30px}
.nav-links{display:flex;align-items:center;gap:2rem;font-size:.93rem;font-weight:500;color:var(--ink-soft)}
.nav-links a{position:relative;padding:.3rem 0}
.nav-links a::after{content:"";position:absolute;left:0;bottom:0;width:0;height:2px;background:var(--grad);border-radius:2px;transition:width .25s ease}
.nav-links a:hover::after{width:100%}
.nav .btn{padding:.65rem 1.3rem;font-size:.9rem}
.menu-btn{display:none;background:none;border:none;cursor:pointer;padding:.4rem}
.menu-btn span{display:block;width:24px;height:2px;background:var(--ink);margin:5px 0;border-radius:2px;transition:.3s}
@media(max-width:920px){
  .nav-links{position:fixed;inset:74px 0 auto 0;background:var(--porcelain);flex-direction:column;align-items:flex-start;gap:0;padding:0 24px;max-height:0;overflow:hidden;transition:max-height .35s ease;border-bottom:1px solid var(--line)}
  .nav-links.open{max-height:420px;padding:12px 24px 24px}
  .nav-links a{padding:.85rem 0;width:100%;border-bottom:1px solid var(--line)}
  .nav-links a:last-of-type{border:none}
  .menu-btn{display:block}
  .menu-btn.open span:nth-child(1){transform:translateY(7px) rotate(45deg)}
  .menu-btn.open span:nth-child(2){opacity:0}
  .menu-btn.open span:nth-child(3){transform:translateY(-7px) rotate(-45deg)}
  .nav-cta-desktop{display:none}
  .nav-links .nav-cta-mobile{display:inline-flex;width:100%;margin-top:1rem;border:none;color:#fff;padding:.85rem 1.3rem}
  .nav-links .nav-cta-mobile::after{display:none}
}
.nav-cta-mobile{display:none}
/* Hero */
.hero{position:relative;padding:184px 0 88px;overflow:hidden}
.hero-grid{position:absolute;inset:0;pointer-events:none;background-image:linear-gradient(to right,rgba(22,24,29,.05) 1px,transparent 1px),linear-gradient(to bottom,rgba(22,24,29,.05) 1px,transparent 1px);background-size:56px 56px;-webkit-mask-image:radial-gradient(ellipse 70% 60% at 50% 38%,#000 35%,transparent 78%);mask-image:radial-gradient(ellipse 70% 60% at 50% 38%,#000 35%,transparent 78%)}
.hero-glow{position:absolute;top:-260px;left:50%;transform:translateX(-50%);width:980px;height:620px;background:radial-gradient(closest-side,rgba(255,140,60,.16),rgba(255,180,46,.07) 55%,transparent 75%);pointer-events:none}
.hero-inner{position:relative;max-width:760px;margin:0 auto;text-align:center}
.hero h1{font-family:var(--body);font-weight:700;letter-spacing:-.02em;font-size:clamp(2.2rem,4.6vw,3.4rem);line-height:1.12;margin:1.5rem 0 1.6rem}
.hero h1 .flame-text{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.hero .lede{font-size:1.08rem;max-width:620px;margin:.2rem auto 2.4rem}
.hero-ctas{display:flex;gap:1rem;flex-wrap:wrap;align-items:center;justify-content:center}
.hero-micro{margin-top:1.8rem;font-size:.86rem;color:var(--ash);display:flex;gap:1.4rem;flex-wrap:wrap;justify-content:center}
.hero .eyebrow::before{display:none}
.hero-micro span{display:inline-flex;align-items:center;gap:.4rem}
.hero-micro svg{width:14px;height:14px;flex:none;stroke:var(--flame-deep)}
.hero-shot{position:relative;max-width:1080px;margin:3.4rem auto 0}
/* Trust */
.trust{padding:42px 0;background:var(--paper);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.trust .label{text-align:center;font-size:.74rem;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--ash);margin-bottom:.9rem}
.trust p{text-align:center;max-width:760px;margin:0 auto;font-family:var(--display);font-weight:500;font-size:clamp(1.05rem,2vw,1.4rem);color:var(--ink);letter-spacing:-.01em}
/* Stats */
.stats{background:var(--night);color:#fff;padding:78px 0}
.stats-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:2rem}
.stat{border-left:1px solid var(--night-line);padding-left:1.6rem}
.stat .num{font-family:var(--display);font-weight:600;font-size:clamp(2.2rem,4vw,3.2rem);line-height:1;background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.stat .cap{margin-top:.55rem;font-size:.92rem;color:rgba(255,255,255,.6)}
@media(max-width:860px){.stats-grid{grid-template-columns:repeat(2,1fr)}}
/* Section heads */
.sec-head{max-width:680px;margin-bottom:3rem}
.sec-head h2{margin:1rem 0 1rem}
.sec-head p{font-size:1.04rem}
.sec-head.center{margin-left:auto;margin-right:auto;text-align:center}
.sec-head.center .eyebrow{justify-content:center}
.sec-head.center .eyebrow::before{display:none}
/* Cards (pains + why) */
.card-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:1.3rem}
.card-grid.two{grid-template-columns:repeat(2,1fr)}
.card{background:var(--paper);border:1px solid var(--line);border-radius:var(--radius);padding:2rem 1.9rem;position:relative;overflow:hidden;transition:transform .3s cubic-bezier(.2,.7,.2,1),box-shadow .3s ease,border-color .3s ease}
.card:hover{transform:translateY(-6px);box-shadow:var(--shadow);border-color:#DDD9D1}
.card-head{display:flex;align-items:center;gap:.85rem;margin-bottom:.7rem}
.card .ico{flex:none;width:42px;height:42px;border-radius:11px;background:linear-gradient(135deg,rgba(255,92,26,.1),rgba(255,180,46,.1));border:1px solid rgba(255,92,26,.16);display:flex;align-items:center;justify-content:center;margin-bottom:1.1rem}
.card-head .ico{margin-bottom:0}
.card .ico .micon{font-family:'Material Symbols Outlined';font-size:23px;line-height:1;color:var(--flame-deep)}
.card-head h3{margin-bottom:0}
.card .n{font-family:var(--display);font-weight:600;color:var(--flame-deep);font-size:1rem;margin-bottom:.5rem}
.card h3{font-size:1.12rem;margin-bottom:.5rem}
.card p{font-size:.95rem}
@media(max-width:900px){.card-grid,.card-grid.two{grid-template-columns:1fr}}
.close-line{text-align:center;max-width:720px;margin:3rem auto 0;font-family:var(--display);font-weight:500;font-size:clamp(1.2rem,2.4vw,1.7rem);color:var(--ink);letter-spacing:-.01em}
.close-line em{font-style:normal;color:var(--flame-deep)}
/* Solution band */
.solution{background:var(--paper);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.solution .inner{max-width:820px;margin:0 auto;text-align:center}
.solution h2{margin:1rem 0 1.4rem}
.solution p{font-size:1.08rem;margin-bottom:1.1rem}
/* Steps */
.proc-list{max-width:880px;margin:0 auto}
.step{display:grid;grid-template-columns:96px 1fr;gap:2rem;padding:2.1rem 0;border-bottom:1px solid var(--line);align-items:start}
.step:last-child{border:none}
.step .no{font-family:var(--display);font-weight:600;font-size:2rem;color:#D9D5CD;line-height:1;transition:color .3s}
.step.in-view .no{color:var(--flame-deep)}
.step h3{margin-bottom:.55rem}
.step p{font-size:.98rem;max-width:620px}
@media(max-width:600px){.step{grid-template-columns:1fr;gap:.6rem}}
/* Compare */
.compare{background:var(--paper);border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.cmp-grid{display:grid;grid-template-columns:1fr 1fr;gap:1.4rem;max-width:940px;margin:0 auto}
.cmp-col{border-radius:var(--radius);padding:2.3rem 2.2rem}
.cmp-col.them{background:var(--porcelain);border:1px solid var(--line)}
.cmp-col.us{background:var(--night);color:#fff;box-shadow:0 28px 60px -28px rgba(14,16,20,.5)}
.cmp-col h3{margin-bottom:1.5rem;font-size:1.1rem;letter-spacing:.02em}
.cmp-col.us h3{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent;display:inline-block}
.cmp-col ul{list-style:none}
.cmp-col li{display:flex;gap:.8rem;align-items:flex-start;padding:.72rem 0;font-size:.96rem;border-bottom:1px solid var(--line)}
.cmp-col.us li{border-bottom:1px solid var(--night-line);color:rgba(255,255,255,.88)}
.cmp-col li:last-child{border:none}
.cmp-col .mark{flex:none;width:20px;height:20px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin-top:.15rem;font-size:.7rem;font-weight:700}
.them .mark{background:#EAE7E1;color:#A9A49B}
.us .mark{background:var(--grad);color:#fff}
@media(max-width:760px){.cmp-grid{grid-template-columns:1fr}}
/* Demo */
.demo .frame{max-width:1080px;margin:0 auto}
.demo .caption{text-align:center;font-size:.9rem;color:var(--ash);margin-top:1.4rem}
/* FAQ */
.faq-list{max-width:760px;margin:0 auto}
.faq{border-bottom:1px solid var(--line)}
.faq button{width:100%;background:none;border:none;cursor:pointer;display:flex;justify-content:space-between;align-items:center;gap:1rem;padding:1.45rem 0;font-family:var(--body);font-size:1.04rem;font-weight:600;color:var(--ink);text-align:left}
.faq button .plus{flex:none;width:26px;height:26px;border-radius:50%;border:1px solid #CFCBC3;display:flex;align-items:center;justify-content:center;font-weight:500;color:var(--ash);transition:transform .3s,background .3s,color .3s,border-color .3s}
.faq.open button .plus{transform:rotate(45deg);background:var(--grad);color:#fff;border-color:transparent}
.faq .ans{max-height:0;overflow:hidden;transition:max-height .35s ease}
.faq .ans p{padding:0 2.4rem 1.5rem 0;font-size:.97rem}
/* CTA / form */
.cta-final{background:var(--night);color:#fff;position:relative;overflow:hidden}
.cta-final::before{content:"";position:absolute;bottom:-220px;left:50%;transform:translateX(-50%);width:900px;height:520px;background:radial-gradient(closest-side,rgba(255,110,30,.18),transparent 72%);pointer-events:none}
.cta-grid{display:grid;grid-template-columns:1fr 1fr;gap:4rem;position:relative;align-items:center}
.cta-left h2{color:#fff;margin:1rem 0 1.1rem}
.cta-left p{color:rgba(255,255,255,.66);max-width:440px;margin-bottom:1.4rem}
.cta-perks{list-style:none;margin-top:1.6rem}
.cta-perks li{display:flex;gap:.8rem;align-items:center;padding:.5rem 0;color:rgba(255,255,255,.8);font-size:.95rem}
.cta-perks .mark{flex:none;width:20px;height:20px;border-radius:50%;background:var(--grad);color:#fff;display:flex;align-items:center;justify-content:center;font-size:.68rem;font-weight:700}
.form-card{background:var(--night-soft);border:1px solid var(--night-line);border-radius:var(--radius);padding:2.2rem}
.form-card h3{color:#fff;margin-bottom:.4rem}
.form-card .sub{color:rgba(255,255,255,.55);font-size:.9rem;margin-bottom:1.6rem}
.field{margin-bottom:1.1rem}
.field label{display:block;font-size:.82rem;font-weight:600;color:rgba(255,255,255,.75);margin-bottom:.4rem}
.field input,.field select,.field textarea{width:100%;background:#0E1014;border:1px solid var(--night-line);border-radius:10px;padding:.8rem .95rem;color:#fff;font-family:var(--body);font-size:.95rem;transition:border-color .2s}
.field input:focus,.field select:focus,.field textarea:focus{outline:none;border-color:var(--flame)}
.field textarea{resize:vertical;min-height:84px}
.form-card .btn{width:100%;margin-top:.4rem}
.form-note{margin-top:.9rem;font-size:.8rem;color:rgba(255,255,255,.45);text-align:center}
@media(max-width:880px){.cta-grid{grid-template-columns:1fr;gap:3rem}}
/* Footer */
footer{background:#0A0C0F;color:rgba(255,255,255,.6);padding:54px 0 32px;font-size:.92rem}
.foot-top{display:flex;justify-content:space-between;gap:2rem;flex-wrap:wrap;align-items:flex-start;margin-bottom:2.4rem}
.foot-brand .logo{color:#fff;margin-bottom:.9rem}
.foot-brand p{color:rgba(255,255,255,.5);max-width:340px;font-size:.9rem}
.foot-bottom{border-top:1px solid var(--night-line);padding-top:1.6rem;display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap;font-size:.84rem;color:rgba(255,255,255,.4)}
/* Reveal */
.reveal{opacity:0;transform:translateY(26px);transition:opacity .7s ease,transform .7s ease}
.reveal.in-view{opacity:1;transform:none}
@media(prefers-reduced-motion:reduce){
  *{animation:none!important;transition:none!important}
  .reveal{opacity:1;transform:none}
  .ember-line::after{transform:scaleX(1)}
  html{scroll-behavior:auto}
}
/* ===== Demo mockup (scoped) ===== */
.gq{background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:0 30px 70px -30px rgba(22,24,29,.4);overflow:hidden}
.gq-chrome{display:flex;align-items:center;gap:.5rem;padding:.7rem 1rem;background:#F3F1ED;border-bottom:1px solid var(--line)}
.gq-dot{width:11px;height:11px;border-radius:50%}
.gq-url{margin-left:.8rem;font-size:.78rem;color:var(--ash);background:#fff;border:1px solid var(--line);border-radius:7px;padding:.25rem .8rem}
.gq-shell{display:grid;grid-template-columns:210px 1fr;min-height:524px}
.gq-side{background:#fff;border-right:1px solid var(--line);padding:1.05rem .85rem;display:flex;flex-direction:column;gap:.18rem}
.gq-brand{display:flex;align-items:center;gap:.55rem;font-family:var(--display);font-weight:600;font-size:1.02rem;color:var(--ink);padding:.1rem .35rem .85rem}
.gq-brand-mark{flex:none;width:26px;height:26px;border-radius:8px;background:var(--grad);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.92rem}
.gq-new{display:flex;align-items:center;gap:.45rem;background:var(--grad);color:#fff;font-weight:600;font-size:.86rem;border-radius:10px;padding:.6rem .8rem;margin-bottom:.65rem;box-shadow:0 10px 20px -12px rgba(232,67,10,.6)}
.gq-new .micon{font-family:'Material Symbols Outlined';font-size:18px}
.gq-nav{display:flex;flex-direction:column;gap:.12rem}
.gq-nav-i{display:flex;align-items:center;gap:.65rem;font-size:.87rem;font-weight:500;color:var(--ash);padding:.52rem .6rem;border-radius:9px}
.gq-nav-i .micon{font-family:'Material Symbols Outlined';font-size:19px;flex:none}
.gq-nav-i.gq-on{background:rgba(255,92,26,.09);color:var(--flame-deep);font-weight:600}
.gq-tag{margin-left:auto;font-size:.68rem;font-weight:700;background:var(--grad);color:#fff;border-radius:99px;padding:.05rem .42rem}
.gq-side-foot{margin-top:auto;display:flex;flex-direction:column;gap:.4rem;padding-top:.6rem;border-top:1px solid var(--line)}
.gq-user{display:flex;align-items:center;gap:.55rem;padding:.25rem .4rem}
.gq-ava{flex:none;width:30px;height:30px;border-radius:50%;background:#16181D;color:#fff;display:flex;align-items:center;justify-content:center;font-size:.72rem;font-weight:700}
.gq-user b{display:block;font-size:.82rem;color:var(--ink);line-height:1.2}
.gq-user i{font-style:normal;font-size:.72rem;color:var(--ash)}
.gq-main{display:flex;flex-direction:column;background:var(--porcelain);min-width:0}
.gq-top{display:flex;align-items:center;justify-content:space-between;gap:1rem;padding:.9rem 1.25rem;background:#fff;border-bottom:1px solid var(--line)}
.gq-crumb{font-size:.73rem;color:var(--ash)}
.gq-crumb b{color:var(--ink-soft);font-weight:600}
.gq-title{display:flex;align-items:center;gap:.55rem;font-family:var(--display);font-weight:600;font-size:1.05rem;color:var(--ink);margin-top:.18rem}
.gq-stat{font-size:.62rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#9A7B00;background:#FFF3D0;border:1px solid #F1DE9B;border-radius:99px;padding:.16rem .5rem}
.gq-top-r{display:flex;align-items:center;gap:.5rem;flex:none}
.gq-tbtn{display:inline-flex;align-items:center;gap:.35rem;font-size:.82rem;font-weight:600;color:var(--ink-soft);border:1px solid var(--line);border-radius:9px;padding:.48rem .85rem;background:#fff;white-space:nowrap}
.gq-tbtn .micon{font-family:'Material Symbols Outlined';font-size:17px}
.gq-tbtn-go{color:#fff;background:var(--grad);border-color:transparent;box-shadow:0 10px 20px -12px rgba(232,67,10,.55)}
.gq-body{display:grid;grid-template-columns:1.5fr 1fr;min-width:0}
.gq-build{padding:1.25rem 1.35rem;border-right:1px solid var(--line);background:#fff;min-width:0}
.gq-build-top{display:flex;justify-content:space-between;gap:1rem;margin-bottom:1.3rem}
.gq-label{display:block;font-size:.68rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--ash);margin-bottom:.5rem}
.gq-evt{display:flex;gap:.45rem;flex-wrap:wrap}
.gq-pill{font-size:.82rem;font-weight:600;color:var(--ink-soft);background:var(--porcelain);border:1px solid var(--line);border-radius:99px;padding:.35rem .85rem}
.gq-pill-on{background:var(--grad);color:#fff;border-color:transparent}
.gq-stepper{display:inline-flex;align-items:center;gap:.7rem;border:1px solid var(--line);border-radius:10px;padding:.3rem .7rem}
.gq-stepper button{border:none;background:none;font-size:1.1rem;color:var(--ash);cursor:default;line-height:1}
.gq-stepper b{font-size:1rem;min-width:30px;text-align:center}
.gq-cat{margin-bottom:1rem}
.gq-cat-head{display:flex;align-items:center;gap:.5rem;font-family:var(--display);font-weight:600;font-size:.95rem;color:var(--ink);margin-bottom:.45rem}
.gq-cat-head .micon{font-family:'Material Symbols Outlined';font-size:18px;color:var(--flame-deep)}
.gq-per{font-size:.66rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--flame-deep);background:rgba(255,92,26,.08);border-radius:99px;padding:.15rem .55rem;margin-left:.2rem}
.gq-line{display:flex;align-items:center;gap:.7rem;padding:.5rem .7rem;border:1px solid var(--line);border-radius:10px;margin-bottom:.4rem;background:#fff;font-size:.9rem}
.gq-check{flex:none;width:18px;height:18px;border-radius:5px;background:var(--grad);color:#fff;display:flex;align-items:center;justify-content:center;font-size:.7rem;font-weight:700}
.gq-name{flex:1;color:var(--ink-soft)}
.gq-name i{font-style:normal;color:var(--ash);font-size:.82rem}
.gq-amt{font-weight:600;color:var(--ink)}
.gq-add{margin-top:.4rem;font-size:.86rem;font-weight:600;color:var(--flame-deep);border:1px dashed #E2BFA8;border-radius:10px;padding:.6rem;text-align:center;background:rgba(255,92,26,.03)}
.gq-sum{padding:1.25rem 1.3rem;background:#fff;display:flex;flex-direction:column;min-width:0}
.gq-sum-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:1.1rem}
.gq-logo{font-family:var(--display);font-weight:600;font-size:1rem;color:var(--ink)}
.gq-logo span{color:var(--flame-deep)}
.gq-badge{display:inline-flex;align-items:center;gap:.35rem;font-size:.62rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--flame-deep);background:rgba(255,92,26,.09);border-radius:99px;padding:.22rem .55rem}
.gq-sum-rows{border-top:1px solid var(--line);padding-top:.6rem}
.gq-row{display:flex;justify-content:space-between;font-size:.9rem;color:var(--ink-soft);padding:.42rem 0}
.gq-row i{font-style:normal;color:var(--ash);font-size:.8rem}
.gq-total{display:flex;justify-content:space-between;align-items:baseline;margin-top:.5rem;padding-top:.9rem;border-top:2px solid var(--ink)}
.gq-total span{font-family:var(--display);font-weight:600;font-size:1rem}
.gq-total b{font-family:var(--display);font-weight:700;font-size:1.55rem;background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.gq-deposit{display:flex;justify-content:space-between;align-items:center;margin-top:.8rem;background:#fff;border:1px solid var(--line);border-radius:10px;padding:.6rem .8rem;font-size:.88rem;color:var(--ink-soft)}
.gq-deposit i{font-style:normal;color:var(--ash);font-size:.8rem}
.gq-deposit b{color:var(--ink)}
.gq-sum-actions{margin-top:auto;padding-top:1.1rem}
.gq-send{display:flex;align-items:center;justify-content:center;gap:.4rem;background:var(--grad);color:#fff;font-weight:600;font-size:.9rem;border-radius:10px;padding:.72rem;box-shadow:0 12px 24px -12px rgba(232,67,10,.55)}
.gq-send .micon{font-family:'Material Symbols Outlined';font-size:17px}
.gq-status{display:flex;align-items:center;justify-content:center;gap:.4rem;margin-top:.7rem;font-size:.77rem;color:var(--ash)}
.gq-status .micon{font-family:'Material Symbols Outlined';font-size:15px}
.gq-live{flex:none;width:7px;height:7px;border-radius:50%;background:#28C840;box-shadow:0 0 0 3px rgba(40,200,64,.18)}
@media(max-width:760px){
  .gq-shell{grid-template-columns:58px 1fr}
  .gq-side{padding:.85rem .45rem}
  .gq-brand{justify-content:center;padding:.1rem 0 .7rem}
  .gq-new{justify-content:center;padding:.6rem 0}
  .gq-nav-i{justify-content:center;padding:.55rem 0}
  .gq-nav-i .gq-tag{display:none}
  .gq-user{justify-content:center;padding:.25rem 0}
  .gq-lbl{display:none}
  .gq-body{grid-template-columns:1fr}
  .gq-build{border-right:none;border-bottom:1px solid var(--line)}
}
/* ===== Small phones ===== */
@media(max-width:520px){
  .wrap{padding:0 18px}
  .eyebrow{font-size:.7rem;letter-spacing:.1em}
  h2{font-size:clamp(1.65rem,7vw,2.1rem)}
  .hero{padding:128px 0 60px}
  .hero h1{font-size:clamp(1.85rem,8vw,2.3rem);line-height:1.16;margin:1.1rem 0 1.1rem}
  .hero .lede{font-size:1rem;margin-bottom:1.7rem}
  .hero-ctas{flex-direction:column;align-items:stretch}
  .hero-ctas .btn{width:100%}
  .hero-micro{gap:.5rem 1.1rem;font-size:.8rem;margin-top:1.4rem}
  .hero-shot{margin-top:2.2rem}
  .trust p{font-size:1.05rem}
  .stats{padding:54px 0}.stats-grid{gap:1.4rem 1.2rem}.stat{padding-left:1.1rem}
  .sec-head{margin-bottom:2rem}.sec-head p{font-size:.98rem}
  .card{padding:1.6rem 1.5rem}
  .close-line{font-size:1.15rem;margin-top:2.2rem}
  .solution p{font-size:1rem}
  .step{padding:1.6rem 0}.step .no{font-size:1.6rem}
  .cmp-col{padding:1.8rem 1.6rem}
  .cta-grid{gap:2.2rem}.cta-left p,.form-card{}
  .form-card{padding:1.6rem 1.4rem}
  .foot-top{flex-direction:column;align-items:flex-start;gap:1.3rem}
  /* demo mockup compaction */
  .gq-chrome{padding:.6rem .8rem}.gq-url{display:none}
  .gq-top{flex-wrap:wrap;padding:.85rem 1rem}
  .gq-top-l{flex:1 1 100%}
  .gq-top-r{flex:1 1 100%}
  .gq-tbtn{flex:1;justify-content:center}
  .gq-build{padding:1.1rem 1rem}.gq-sum{padding:1.1rem 1rem}
  .gq-build-top{gap:.8rem}
  .gq-line{font-size:.82rem;gap:.5rem;padding:.45rem .6rem}
  .gq-name i{display:block;margin-top:.05rem}
  .gq-cat-head{font-size:.88rem}
  .gq-total b{font-size:1.3rem}
  .gq-deposit{font-size:.82rem}
}
"""

# ---------------------------------------------------------------- JS (shared)
JS = r"""
const header=document.getElementById('header');
addEventListener('scroll',()=>header.classList.toggle('scrolled',scrollY>10),{passive:true});
const menuBtn=document.getElementById('menuBtn'),navLinks=document.getElementById('navLinks');
menuBtn.addEventListener('click',()=>{const open=navLinks.classList.toggle('open');menuBtn.classList.toggle('open',open);menuBtn.setAttribute('aria-expanded',open);});
navLinks.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{navLinks.classList.remove('open');menuBtn.classList.remove('open');menuBtn.setAttribute('aria-expanded','false');}));
const io=new IntersectionObserver(es=>{es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in-view');io.unobserve(e.target);}});},{threshold:.18});
document.querySelectorAll('.reveal,.step,.sec-head').forEach(el=>io.observe(el));
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
const cio=new IntersectionObserver(es=>{es.forEach(e=>{if(!e.isIntersecting)return;cio.unobserve(e.target);const t=+e.target.dataset.target;if(reduce){e.target.textContent=t;return;}const s=performance.now(),d=1400;const tick=n=>{const p=Math.min((n-s)/d,1);e.target.textContent=Math.round(t*(1-Math.pow(1-p,3)));if(p<1)requestAnimationFrame(tick);};requestAnimationFrame(tick);});},{threshold:.5});
document.querySelectorAll('.count').forEach(el=>cio.observe(el));
document.querySelectorAll('.faq').forEach(faq=>{const b=faq.querySelector('button'),a=faq.querySelector('.ans');b.addEventListener('click',()=>{document.querySelectorAll('.faq.open').forEach(o=>{if(o!==faq){o.classList.remove('open');o.querySelector('.ans').style.maxHeight=null;o.querySelector('button').setAttribute('aria-expanded','false');}});const open=faq.classList.toggle('open');a.style.maxHeight=open?a.scrollHeight+'px':null;b.setAttribute('aria-expanded',open);});});
const f=document.getElementById('leadForm');
if(f){const st=document.getElementById('formStatus'),bt=f.querySelector('button[type="submit"]');
f.addEventListener('submit',async e=>{e.preventDefault();bt.disabled=true;const o=bt.textContent;bt.textContent='Sending…';st.style.color='';
try{const r=await fetch(f.action,{method:'POST',headers:{'Accept':'application/json'},body:new FormData(f)});const d=await r.json();
if(r.ok&&d.success){f.reset();st.textContent="Thanks, your request is in. We'll reply within one business day.";st.style.color='var(--ember)';}
else{throw new Error(d.message||'failed');}}catch(err){st.textContent='Something went wrong. Please email us directly.';st.style.color='#ff8a5c';}
finally{bt.disabled=false;bt.textContent=o;}});}
"""

# The agency behind every niche page (shown in the nav bar + footer, links out
# to the main site). The product brand (cfg["brand"]) stays in the page copy.
VENDOR_NAME = "White Phoenix"
VENDOR_URL = "https://whitephoenixconsulting.com/"

LOGO_SVG = (
    '<svg viewBox="0 0 32 32" fill="none" aria-hidden="true">'
    '<path d="M16 2C16 2 8 9 8 17a8 8 0 0 0 16 0c0-3-1.4-5.4-3-7.4.4 2 .2 4-1.4 5.4.6-3.4-1-7.6-3.6-13Z" fill="url(#fg)"/>'
    '<path d="M16 30c-3 0-5.4-1.4-6.9-3.5C10.6 27.4 13 28 16 28s5.4-.6 6.9-1.5C21.4 28.6 19 30 16 30Z" fill="#16181D"/>'
    '<defs><linearGradient id="fg" x1="8" y1="2" x2="24" y2="25"><stop stop-color="#FF5C1A"/>'
    '<stop offset="1" stop-color="#FFB42E"/></linearGradient></defs></svg>'
)
CHECK_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>'


def render(cfg, demo_html):
    b = esc(cfg["brand"])
    m = cfg["meta"]
    url = f'{cfg["domain"]}/lp/{cfg["slug"]}.html'

    nav_links = "".join(
        f'<a href="{esc(l["href"])}">{esc(l["label"])}</a>' for l in cfg["nav"]["links"]
    )
    micro = "".join(
        f'<span>{CHECK_SVG}{esc(t)}</span>' for t in cfg["hero"]["micro"]
    )
    stats = "".join(
        f'<div class="stat reveal"><div class="num"><span class="count" data-target="{esc(s["num"])}">0</span>{esc(s["suffix"])}</div>'
        f'<div class="cap">{esc(s["cap"])}</div></div>'
        for s in cfg["stats"]
    )
    pains = "".join(
        f'<div class="card reveal"><div class="card-head"><div class="ico"><span class="micon">{esc(p["icon"])}</span></div><h3>{esc(p["title"])}</h3></div><p>{esc(p["body"])}</p></div>'
        for p in cfg["problem"]["pains"]
    )
    steps = "".join(
        f'<div class="step"><div class="no">0{i}</div><div><h3>{esc(s["title"])}</h3><p>{esc(s["body"])}</p></div></div>'
        for i, s in enumerate(cfg["steps"], 1)
    )
    whys = "".join(
        f'<div class="card reveal"><div class="n">0{i}</div><h3>{esc(w["title"])}</h3><p>{esc(w["body"])}</p></div>'
        for i, w in enumerate(cfg["why"], 1)
    )
    cmp_them = "".join(
        f'<li><span class="mark">✕</span>{esc(x)}</li>' for x in cfg["compare"]["them"]
    )
    cmp_us = "".join(
        f'<li><span class="mark">✓</span>{esc(x)}</li>' for x in cfg["compare"]["us"]
    )
    faqs = "".join(
        f'<div class="faq"><button aria-expanded="false"><span>{esc(q["q"])}</span><span class="plus">+</span></button>'
        f'<div class="ans"><p>{esc(q["a"])}</p></div></div>'
        for q in cfg["faqs"]
    )
    fm = cfg["form"]
    fin = cfg["final"]

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(m["title"])}</title>
<meta name="description" content="{esc(m["description"])}">
<link rel="canonical" href="{esc(url)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0E1014">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{b}">
<meta property="og:url" content="{esc(url)}">
<meta property="og:title" content="{esc(m["title"])}">
<meta property="og:description" content="{esc(m["description"])}">
<meta property="og:image" content="{esc(m["og_image"])}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(m["title"])}">
<meta name="twitter:description" content="{esc(m["description"])}">
<meta name="twitter:image" content="{esc(m["og_image"])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link href="https://api.fontshare.com/v2/css?f[]=clash-display@500,600,700&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,500,0,0&display=swap" rel="stylesheet">
<style>{CSS}</style>
</head>
<body>

<header id="header">
  <div class="wrap nav">
    <a href="{VENDOR_URL}" class="logo" aria-label="{VENDOR_NAME} main website">{LOGO_SVG}{VENDOR_NAME}</a>
    <nav class="nav-links" id="navLinks" aria-label="Main navigation">{nav_links}<a href="#book" class="btn btn-flame nav-cta-mobile">{esc(cfg["nav"]["cta"])}</a></nav>
    <a href="#book" class="btn btn-flame nav-cta-desktop">{esc(cfg["nav"]["cta"])}</a>
    <button class="menu-btn" id="menuBtn" aria-label="Toggle menu" aria-expanded="false"><span></span><span></span><span></span></button>
  </div>
</header>

<main id="top">

<!-- HERO -->
<section class="hero">
  <div class="hero-grid" aria-hidden="true"></div>
  <div class="hero-glow" aria-hidden="true"></div>
  <div class="wrap">
    <div class="hero-inner reveal in-view">
      <span class="eyebrow">{esc(cfg["hero"]["eyebrow"])}</span>
      <h1>{esc(cfg["hero"]["headline"])} <span class="flame-text">{esc(cfg["hero"]["headline_accent"])}</span></h1>
      <p class="lede">{esc(cfg["hero"]["sub"])}</p>
      <div class="hero-ctas">
        <a href="#book" class="btn btn-flame">{esc(cfg["hero"]["cta_primary"])}</a>
        <a href="#how" class="btn btn-ghost">{esc(cfg["hero"]["cta_secondary"])}</a>
      </div>
      <div class="hero-micro">{micro}</div>
    </div>
    <div class="hero-shot">{demo_html}</div>
  </div>
</section>

<!-- TRUST -->
<section class="trust">
  <div class="wrap">
    <div class="label">{esc(cfg["trust"]["label"])}</div>
    <p>{esc(cfg["trust"]["line"])}</p>
  </div>
</section>

<!-- STATS -->
<section class="stats">
  <div class="wrap"><div class="stats-grid">{stats}</div></div>
</section>

<!-- PROBLEM -->
<section id="problem">
  <div class="wrap">
    <div class="sec-head center">
      <span class="eyebrow">The problem</span>
      <h2><span class="ember-line">{esc(cfg["problem"]["heading"])}</span></h2>
      <p>{esc(cfg["problem"]["intro"])}</p>
    </div>
    <div class="card-grid">{pains}</div>
    <p class="close-line">{esc(cfg["problem"]["close"])}</p>
  </div>
</section>

<!-- SOLUTION -->
<section class="solution">
  <div class="wrap"><div class="inner">
    <span class="eyebrow" style="justify-content:center">The solution</span>
    <h2><span class="ember-line">{esc(cfg["solution"]["heading"])}</span></h2>
    <p>{esc(cfg["solution"]["body"])}</p>
    <p>{esc(cfg["solution"]["body2"])}</p>
  </div></div>
</section>

<!-- HOW IT WORKS -->
<section id="how">
  <div class="wrap">
    <div class="sec-head center">
      <span class="eyebrow">How it works</span>
      <h2><span class="ember-line">{esc(cfg["steps_heading"])}</span></h2>
    </div>
    <div class="proc-list">{steps}</div>
  </div>
</section>

<!-- WHY -->
<section id="why" class="solution">
  <div class="wrap">
    <div class="sec-head center">
      <span class="eyebrow">Why switch</span>
      <h2><span class="ember-line">{esc(cfg["why_heading"])}</span></h2>
    </div>
    <div class="card-grid two">{whys}</div>
  </div>
</section>

<!-- DEMO -->
<section id="demo" class="demo">
  <div class="wrap">
    <div class="sec-head center">
      <span class="eyebrow">Interactive demo</span>
      <h2><span class="ember-line">{esc(cfg["demo"]["heading"])}</span></h2>
      <p>{esc(cfg["demo"]["sub"])}</p>
    </div>
    <div class="frame reveal">{demo_html}</div>
    <p class="caption">{esc(cfg["demo"]["caption"])}</p>
  </div>
</section>

<!-- COMPARE -->
<section class="compare">
  <div class="wrap">
    <div class="sec-head center">
      <span class="eyebrow">How we're different</span>
      <h2><span class="ember-line">{esc(cfg["compare"]["heading"])}</span></h2>
      <p>{esc(cfg["compare"]["sub"])}</p>
    </div>
    <div class="cmp-grid">
      <div class="cmp-col them reveal"><h3>{esc(cfg["compare"]["them_title"])}</h3><ul>{cmp_them}</ul></div>
      <div class="cmp-col us reveal"><h3>{esc(cfg["compare"]["us_title"])}</h3><ul>{cmp_us}</ul></div>
    </div>
  </div>
</section>

<!-- FAQ -->
<section id="faq">
  <div class="wrap">
    <div class="sec-head center">
      <span class="eyebrow">FAQ</span>
      <h2><span class="ember-line">{esc(cfg["faq_heading"])}</span></h2>
    </div>
    <div class="faq-list">{faqs}</div>
  </div>
</section>

<!-- FINAL CTA + FORM -->
<section id="book" class="cta-final">
  <div class="wrap"><div class="cta-grid">
    <div class="cta-left reveal">
      <span class="eyebrow" style="color:var(--ember)">{esc(b)}</span>
      <h2><span class="ember-line">{esc(fin["heading"])}</span></h2>
      <p>{esc(fin["sub"])}</p>
      <ul class="cta-perks">
        <li><span class="mark">✓</span>Fully customized to your business: services, pricing &amp; brand</li>
        <li><span class="mark">✓</span>Once it's custom-built, we hand it over to you to run</li>
        <li><span class="mark">✓</span>{esc(fin["reassurance"])}</li>
      </ul>
    </div>
    <div class="form-card reveal">
      <h3>{esc(fin["form_title"])}</h3>
      <p class="sub">{esc(fin["form_sub"])}</p>
      <form id="leadForm" action="https://api.web3forms.com/submit" method="POST">
        <input type="hidden" name="access_key" value="{esc(fm["access_key"])}">
        <input type="hidden" name="subject" value="{esc(fm["subject"])}">
        <input type="hidden" name="from_name" value="{b} Landing Page">
        <input type="checkbox" name="botcheck" style="display:none" tabindex="-1" autocomplete="off">
        <div class="field"><label for="name">Your name</label><input id="name" name="name" required placeholder="Jordan Smith"></div>
        <div class="field"><label for="company">Company</label><input id="company" name="company" placeholder="Smith Events Co."></div>
        <div class="field"><label for="email">Work email</label><input id="email" name="email" type="email" required placeholder="you@yourcompany.com"></div>
        <div class="field"><label for="events">Events per month</label>
          <select id="events" name="events_per_month">
            <option value="1-5">1–5</option><option value="6-15">6–15</option>
            <option value="16-40">16–40</option><option value="40+">40+</option>
          </select>
        </div>
        <div class="field"><label for="msg">Anything we should know? (optional)</label><textarea id="msg" name="message" placeholder="Event types you quote, current tools, biggest headache…"></textarea></div>
        <button type="submit" class="btn btn-flame">{esc(cfg["nav"]["cta"])}</button>
        <p class="form-note" id="formStatus">{esc(fin["reassurance"])}</p>
      </form>
    </div>
  </div></div>
</section>

</main>

<footer>
  <div class="wrap">
    <div class="foot-top">
      <div class="foot-brand">
        <a href="{VENDOR_URL}" class="logo">{LOGO_SVG}{VENDOR_NAME}</a>
        <p>{esc(cfg["footer_tagline"])}</p>
      </div>
      <a href="#book" class="btn btn-night">{esc(cfg["nav"]["cta"])}</a>
    </div>
    <div class="foot-bottom">
      <span>© 2026 {VENDOR_NAME}. All rights reserved.</span>
      <span>Made for US event professionals.</span>
    </div>
  </div>
</footer>

<script>{JS}</script>
</body>
</html>
"""


def build_one(path):
    cfg = json.loads(path.read_text())
    demo_path = NICHES / cfg["demo"]["partial"]
    demo_html = demo_path.read_text() if demo_path.exists() else ""
    OUT.mkdir(exist_ok=True)
    out_file = OUT / f'{cfg["slug"]}.html'
    out_file.write_text(render(cfg, demo_html))
    print(f"  ✓ {path.name}  →  lp/{cfg['slug']}.html  ({out_file.stat().st_size//1024} KB)")


def main():
    targets = sys.argv[1:]
    configs = sorted(NICHES.glob("*.json"))
    if targets:
        configs = [NICHES / f"{t}.json" for t in targets]
    print("Building niche landing pages…")
    for c in configs:
        if not c.exists():
            print(f"  ! missing {c.name}")
            continue
        build_one(c)
    print("Done.")


if __name__ == "__main__":
    main()
