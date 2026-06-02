#!/usr/bin/env python3
"""Παράγει το AE006/index.html από το AE007/index.html.

AE006 = ίδια δομή με AE007 (Unit Linked + ασφαλιστικός πράκτορας), αλλά σε κάθε ερώτηση
εμφανίζεται μόνο η σωστή απάντηση — χωρίς τυχαία σειρά απαντήσεων / πολλαπλές επιλογές.

Τρέξτε από τη ρίζα του repo:
  python3 AE006/build_ae006.py
"""
from __future__ import annotations

import re
import shutil
from pathlib import Path

AE007 = Path(__file__).resolve().parent.parent / "AE007"
AE006 = Path(__file__).resolve().parent
OUT = AE006 / "index.html"
SRC = AE007 / "index.html"


def main() -> None:
    if not SRC.is_file():
        raise SystemExit(f"Δεν βρέθηκε πηγή: {SRC}")

    text = SRC.read_text(encoding="utf-8")

    text = text.replace("ae007_ul_quiz_state_v1", "ae006_ul_quiz_state_v1")
    text = text.replace(
        "/* Στυλιανός — AE007: έκδοση επίδειξης· Unit Linked + πράκτορας (χωρίς μεσίτη / χωρίς ύλη κεφαλαιαγοράς). */",
        "/* AE006: Unit Linked + πράκτορας — μόνο σωστή απάντηση ανά ερώτηση (χωρίς τυχαία σειρά απαντήσεων). */",
    )
    text = text.replace(
        "/* ——— Ασφαλιστικός πράκτορας: insurance_agent_yli/ (AE007) ——— */",
        "/* ——— Ασφαλιστικός πράκτορας: insurance_agent_yli/ (AE006) ——— */",
    )

    # Αφαίρεση checkbox «Τυχαία σειρά απαντήσεων»
    for block in (
        """        <label class="quiz-check" style="display:flex;align-items:center;gap:8px;margin-top:6px;cursor:pointer;font-size:15px">
          <input type="checkbox" id="catShuffleAns">
          Τυχαία σειρά απαντήσεων
        </label>
""",
        """          <label class="quiz-check" style="display:flex;align-items:center;gap:8px;margin-top:6px;cursor:pointer;font-size:15px">
            <input type="checkbox" id="qmPraShuffleAns">
            Τυχαία σειρά απαντήσεων
          </label>
""",
        """      <label class="quiz-check" style="display:flex;align-items:center;gap:8px;margin-top:6px;cursor:pointer;font-size:15px">
        <input type="checkbox" id="praShuffleAns">
        Τυχαία σειρά απαντήσεων
      </label>
""",
    ):
        text = text.replace(block, "")

    # CSS: μπλοκ μόνο-σωστής απάντησης
    text = text.replace(
        ".opt{padding:13px 16px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);",
        ".ans-only{padding:14px 16px;border-radius:10px;border:1px solid rgba(29,158,117,0.45);"
        "background:rgba(29,158,117,0.12);color:var(--teal3);font-size:15px;line-height:1.55;margin-bottom:12px}\n"
        ".ans-only.seen{opacity:1}\n"
        ".ans-continue-btn{margin-top:4px}\n"
        ".opt{padding:13px 16px;border-radius:10px;border:1px solid rgba(255,255,255,0.1);",
    )
    text = text.replace(
        'html[data-time-theme="day"] .opt{background:rgba(255,255,255,0.7);',
        'html[data-time-theme="day"] .ans-only{background:rgba(29,158,117,0.1);border-color:rgba(15,110,86,0.35);color:var(--teal2)}\n'
        'html[data-time-theme="day"] .opt{background:rgba(255,255,255,0.7);',
    )

    # Βοηθητική + απλοποίηση σειράς απαντήσεων
    text = text.replace(
        "function shuffle(arr){const a=[...arr];",
        "function correctAnswerText(q){\n"
        '  const k=q&&q.correct;\n'
        '  return k&&q.options&&q.options[k]!=null?String(q.options[k]).trim():"";\n'
        "}\n"
        "function shuffle(arr){const a=[...arr];",
    )

    text = text.replace(
        "function optionKeysForQuestion(q,idx){\n"
        '  const base=["α","β","γ","δ"].filter(k=>q.options&&q.options[k]);\n'
        "  if(!qShuffleAnswers)return base;\n"
        "  if(qOptOrderByIdx[idx]!==undefined)return qOptOrderByIdx[idx];\n"
        "  const shuffled=shuffle(base.slice());\n"
        "  qOptOrderByIdx[idx]=shuffled;\n"
        "  return shuffled;\n"
        "}",
        "function optionKeysForQuestion(q,idx){\n"
        '  if(q&&q.correct&&q.options&&q.options[q.correct])return [q.correct];\n'
        '  return ["α","β","γ","δ"].filter(k=>q.options&&q.options[k]);\n'
        "}",
    )

    text = text.replace(
        "  qShuffleQuestionOrder=!!document.getElementById(\"catShuffleQ\").checked;\n"
        "  qShuffleAnswers=!!document.getElementById(\"catShuffleAns\").checked;\n",
        "  qShuffleQuestionOrder=!!document.getElementById(\"catShuffleQ\").checked;\n"
        "  qShuffleAnswers=false;\n",
    )

    text = text.replace(
        "function quizFeedbackHtml(ok,q,orderKeys,chosenIdx){\n"
        "  const exp=String(q.explanation||\"\").trim();\n"
        "  const solD=quizSolutionDetailsHtml(q);\n"
        "  if(ok){\n"
        "    return (\n"
        "      exp\n"
        "        ? `<p class=\"quiz-fb-line\">✓ Σωστά!</p><p class=\"quiz-fb-exp\">${htmlEsc(exp)}</p>`\n"
        "        : `<p class=\"quiz-fb-line\">✓ Σωστά!</p>`\n"
        "    )+solD;\n"
        "  }\n"
        "  const wrongL=(chosenIdx>=0&&chosenIdx<orderKeys.length)?orderKeys[chosenIdx]:\"—\";\n"
        "  const rightL=q.correct||\"—\";\n"
        "  const rt=(q.options&&q.options[rightL])?String(q.options[rightL]).trim():\"\";\n"
        "  const rtShort=rt?htmlEsc(rt.length>130?rt.slice(0,127)+\"…\":rt):\"\";\n"
        "  const line=`✗ Λάθος. Επέλεξες την <strong>${htmlEsc(String(wrongL))}</strong> — δεν είναι η σωστή. Η σωστή απάντηση είναι η <strong>${htmlEsc(String(rightL))}</strong>${rtShort?\": \"+rtShort:\"\"}.`;\n"
        "  const expP=exp?`<p class=\"quiz-fb-exp\">${htmlEsc(exp)}</p>`:\"\";\n"
        "  return `<p class=\"quiz-fb-line\">${line}</p>`+expP+solD;\n"
        "}",
        "function quizFeedbackHtml(ok,q,orderKeys,chosenIdx){\n"
        "  const exp=String(q.explanation||\"\").trim();\n"
        "  const solD=quizSolutionDetailsHtml(q);\n"
        "  const rt=correctAnswerText(q);\n"
        "  const head=rt?`<p class=\"quiz-fb-line\">✓ Σωστή απάντηση: ${htmlEsc(rt)}</p>`:`<p class=\"quiz-fb-line\">✓ Σωστή απάντηση</p>`;\n"
        "  const expP=exp?`<p class=\"quiz-fb-exp\">${htmlEsc(exp)}</p>`:\"\";\n"
        "  return head+expP+solD;\n"
        "}",
    )

    # renderQ — μόνο σωστή απάντηση
    old_render_q = """function renderQ(){
  if(qIdx>=qList.length){finishQuiz();return;}
  const q=qList[qIdx];
  const orderKeys=optionKeysForQuestion(q,qIdx);
  const opts=orderKeys.map(k=>q.options[k]);
  const correctIdx=orderKeys.indexOf(q.correct);
  const prev=qAnsByIdx[qIdx];
  qAns=!!prev;
  document.getElementById("qFill").style.width=Math.round(qIdx/qList.length*100)+"%";
  document.getElementById("qLbl").textContent=(qIdx+1)+"/"+qList.length;
  let optHtml;
  let fbHtml;
  optHtml=prev?opts.map((o,i)=>{
    let cls="opt dis";
    if(i===correctIdx)cls+=" ok";
    else if(i===prev.i)cls+=" ko";
    return `<button class="${cls}">${o}</button>`;
  }).join(""):opts.map((o,i)=>`<button class="opt" onclick="ans(${i})">${o}</button>`).join("");
  fbHtml=prev?`<div class="fbbox ${prev.ok?"":"ko"}" id="fb" style="display:block">${quizFeedbackHtml(prev.ok,q,orderKeys,prev.i)}</div>`:`<div class="fbbox" id="fb"></div>`;
  const qidBadge=(q.id!=null&&String(q.id).length)?`<span class="qjsonid" title="${htmlEsc("Αναγνωριστικό id στο αρχείο questions_bank.json")}">${htmlEsc(String(q.id))}</span>`:"";
  document.getElementById("qArea").innerHTML=`<div class="qcard">
    <div class="qmeta qmeta-row-split">
      <div class="qmeta-main"><span class="qmetatag" title="${htmlEsc(q.chapter||"")}">${htmlEsc(chapterShortLabel(q.chapter))}</span>${qidBadge}<span class="qmetatag">${q.difficultyStr||""}</span><span class="qmetatag" title="${(q.topic||"").slice(0,80)}">${(q.topic||"").slice(0,30)}${(q.topic||"").length>30?"…":""}</span></div>
      <div class="qmeta-tts-inline"></div>
    </div>
    <div class="qtag">Ερώτηση ${qIdx+1} από ${qList.length}</div>
    <div class="qtext">${q.text}</div>
    <div class="opts">${optHtml}</div>
    ${fbHtml}
  </div>`;
  document.getElementById("qNavPrev").style.display=prev&&qIdx>0?"inline-block":"none";
  document.getElementById("qNavNext").style.display=prev?"inline-block":"none";
}"""

    new_render_q = """function markUlQuestionSeen(){
  if(!qList.length||qIdx<0||qIdx>=qList.length)return;
  if(!qAnsByIdx[qIdx]){
    qAnsByIdx[qIdx]={i:0,correctIdx:0,ok:true};
    qScore++;
  }
  qAns=true;
  if(qTimerId){pauseTimer();}
}

function renderQ(){
  if(qIdx>=qList.length){finishQuiz();return;}
  const q=qList[qIdx];
  const ansText=correctAnswerText(q)||"—";
  markUlQuestionSeen();
  document.getElementById("qFill").style.width=Math.round(qIdx/qList.length*100)+"%";
  document.getElementById("qLbl").textContent=(qIdx+1)+"/"+qList.length;
  const ansBlock=`<div class="ans-only seen">${htmlEsc(ansText)}</div>`;
  const qidBadge=(q.id!=null&&String(q.id).length)?`<span class="qjsonid" title="${htmlEsc("Αναγνωριστικό id στο αρχείο questions_bank.json")}">${htmlEsc(String(q.id))}</span>`:"";
  document.getElementById("qArea").innerHTML=`<div class="qcard">
    <div class="qmeta qmeta-row-split">
      <div class="qmeta-main"><span class="qmetatag" title="${htmlEsc(q.chapter||"")}">${htmlEsc(chapterShortLabel(q.chapter))}</span>${qidBadge}<span class="qmetatag">${q.difficultyStr||""}</span><span class="qmetatag" title="${(q.topic||"").slice(0,80)}">${(q.topic||"").slice(0,30)}${(q.topic||"").length>30?"…":""}</span></div>
      <div class="qmeta-tts-inline"></div>
    </div>
    <div class="qtag">Ερώτηση ${qIdx+1} από ${qList.length}</div>
    <div class="qtext">${q.text}</div>
    <div class="slbl" style="margin-top:12px;margin-bottom:8px">Σωστή απάντηση</div>
    ${ansBlock}
  </div>`;
  document.getElementById("qNavPrev").style.display=qIdx>0?"inline-block":"none";
  document.getElementById("qNavNext").style.display="inline-block";
}"""

    if old_render_q not in text:
        raise SystemExit("renderQ block not found")
    text = text.replace(old_render_q, new_render_q)

    text = text.replace(
        "function ans(i){\n"
        "  if(qAns)return;qAns=true;\n"
        "  const q=qList[qIdx];\n"
        "  const orderKeys=optionKeysForQuestion(q,qIdx);\n"
        "  const correctIdx=orderKeys.indexOf(q.correct);\n"
        "  const ok=i===correctIdx;\n"
        "  qAnsByIdx[qIdx]={i,correctIdx,ok};\n"
        "  if(ok)qScore++;\n"
        "  pauseTimer();\n"
        "  const qOpts=document.querySelectorAll(\"#qArea .opt\");\n"
        "  qOpts.forEach(o=>o.classList.add(\"dis\"));\n"
        "  if(correctIdx>=0&&correctIdx<qOpts.length)qOpts[correctIdx].classList.add(\"ok\");\n"
        "  if(!ok&&i>=0&&i<qOpts.length)qOpts[i].classList.add(\"ko\");\n"
        "  const fb=document.getElementById(\"fb\");fb.style.display=\"block\";fb.classList.toggle(\"ko\",!ok);\n"
        "  fb.innerHTML=quizFeedbackHtml(ok,q,orderKeys,i);\n"
        "  document.getElementById(\"qNavPrev\").style.display=qIdx>0?\"inline-block\":\"none\";\n"
        "  document.getElementById(\"qNavNext\").style.display=\"inline-block\";\n"
        "  saveUlQuizState();\n"
        "}",
    text = text.replace(
        "function ansReveal(){\n"
        "  if(qAns)return;\n"
        "  qAns=true;\n"
        "  qAnsByIdx[qIdx]={i:0,correctIdx:0,ok:true};\n"
        "  qScore++;\n"
        "  pauseTimer();\n"
        "  renderQ();\n"
        "  saveUlQuizState();\n"
        "}\n\n",
        "",
    )
    text = text.replace(
        "function quizNext(){\n"
        "  if(qIdx>=qList.length-1){finishQuiz();return;}\n"
        "  qIdx++;\n"
        "  const isAnswered=qAnsByIdx[qIdx];\n"
        "  if(!isAnswered&&document.getElementById(\"qTimer\").style.display!==\"none\")resumeTimer();\n"
        "  renderQ();\n"
        "  saveUlQuizState();\n"
        "}",
        "function quizNext(){\n"
        "  saveUlQuizState();\n"
        "  if(qIdx>=qList.length-1){finishQuiz();return;}\n"
        "  qIdx++;\n"
        "  renderQ();\n"
        "  saveUlQuizState();\n"
        "}",
    )

    # Αφαίρεση ανακάτεμα απαντήσεων πράκτορα κατά φόρτωση
    text = text.replace(
        "      const elQ=document.getElementById(sid+\"ShuffleQ\");\n"
        "      const elA=document.getElementById(sid+\"ShuffleAns\");\n"
        "      const wantQ=elQ&&elQ.checked;\n"
        "      const wantA=elA&&elA.checked;\n"
        "      if(wantQ){\n"
        "        for(let i=list.length-1;i>0;i--){\n"
        "          const j=Math.floor(Math.random()*(i+1));\n"
        "          const t=list[i];list[i]=list[j];list[j]=t;\n"
        "        }\n"
        "        ctx._mesShuffledQ=true;\n"
        "      }\n"
        "      if(wantA){\n"
        "        ctx.shuffleAns=true;\n"
        "        list.forEach((q,qi)=>{\n"
        "          const base=yliOptOrderBase(q);\n"
        "          const perm=base.slice();\n"
        "          for(let i=perm.length-1;i>0;i--){\n"
        "            const j=Math.floor(Math.random()*(i+1));\n"
        "            const x=perm[i];perm[i]=perm[j];perm[j]=x;\n"
        "          }\n"
        "          ctx.optOrderByIdx[qi]=perm;\n"
        "        });\n"
        "      }\n",
        "      const elQ=document.getElementById(sid+\"ShuffleQ\");\n"
        "      const wantQ=elQ&&elQ.checked;\n"
        "      if(wantQ){\n"
        "        for(let i=list.length-1;i>0;i--){\n"
        "          const j=Math.floor(Math.random()*(i+1));\n"
        "          const t=list[i];list[i]=list[j];list[j]=t;\n"
        "        }\n"
        "        ctx._mesShuffledQ=true;\n"
        "      }\n",
    )

    text = text.replace(
        "function yliOptOrder(q,qIdx){\n"
        "  const ctx=yliAct;\n"
        "  const ix=qIdx!=null&&Number.isFinite(qIdx)?qIdx:ctx.idx;\n"
        "  if(insuranceAuxCtx(ctx)&&ctx.shuffleAns&&ctx.optOrderByIdx&&ctx.optOrderByIdx[ix]){\n"
        "    return ctx.optOrderByIdx[ix];\n"
        "  }\n"
        "  return yliOptOrderBase(q);\n"
        "}",
        "function yliOptOrder(q,qIdx){\n"
        "  if(q&&q.correct&&q.options&&q.options[q.correct])return [q.correct];\n"
        "  return yliOptOrderBase(q);\n"
        "}",
    )

    text = text.replace(
        "function yliFeedbackHtml(ok,q,chosenIdx){\n"
        "  const extra=yliExtraExplainHtml(q);\n"
        "  if(ok)return `<p class=\"quiz-fb-line\">✓ Σωστά!</p>`+extra;\n"
        "  const order=yliOptOrder(q,yliAct.idx);\n"
        "  const wrongL=(chosenIdx>=0&&chosenIdx<order.length)?order[chosenIdx]:\"—\";\n"
        "  const L=q.correct||\"\";\n"
        "  const optText=q.options&&q.options[L]?String(q.options[L]).trim():\"\";\n"
        "  const escL=yliEsc(L);\n"
        "  const preview=optText?yliEsc(optText.length>160?optText.slice(0,157)+\"…\":optText):\"\";\n"
        "  const body=preview\n"
        "    ? `Η σωστή απάντηση είναι η <strong>${escL}</strong>: ${preview}`\n"
        "    : `Η σωστή απάντηση είναι η <strong>${escL}</strong>.`;\n"
        "  return `<p class=\"quiz-fb-line\">✗ Λάθος. Επέλεξες την <strong>${yliEsc(wrongL)}</strong> — δεν είναι η σωστή. ${body}</p>`+extra;\n"
        "}",
        "function yliFeedbackHtml(ok,q,chosenIdx){\n"
        "  const extra=yliExtraExplainHtml(q);\n"
        "  const optText=correctAnswerText(q);\n"
        "  const head=optText?`<p class=\"quiz-fb-line\">✓ Σωστή απάντηση: ${yliEsc(optText)}</p>`:`<p class=\"quiz-fb-line\">✓ Σωστή απάντηση</p>`;\n"
        "  return head+extra;\n"
        "}",
    )

    yli_render_block = """  const q=ctx.list[ctx.idx];
  const order=yliOptOrder(q,ctx.idx);
  const opts=order.map(k=>q.options[k]);
  const correctIdx=order.indexOf(q.correct);
  const prev=ctx.ans[ctx.idx];
  const answered=!!prev;
  fill.style.width=Math.round(ctx.idx/ctx.list.length*100)+"%";
  lbl.textContent=(ctx.idx+1)+"/"+ctx.list.length;
  const sheetTag=q.sheetName?`<span class="qmetatag">${yliEsc(q.sheetName)}</span>`:"";
  const chapTag=q.chapter?`<span class="qmetatag" title="${yliEsc(q.topic||q.chapter)}">${yliEsc(q.chapter)}</span>`:"";
  const yliJsonKey=q.id!=null&&String(q.id).length?"id":"n";
  const yliJsonVal=q.id!=null&&String(q.id).length?q.id:q.n;
  const yliIdBadge=yliJsonVal!=null&&String(yliJsonVal).length?`<span class="qjsonid" title="${yliEsc(yliJsonKey==="id"?"Αναγνωριστικό id στο JSON αυτού του αρχείου":"Αριθμός n (σειρά ερώτησης) στο JSON αυτού του αρχείου")}">${yliEsc(String(yliJsonVal))}</span>`:"";
  const headTag=q.headerTitle?`<span class="qmetatag" title="${yliEsc(q.headerTitle)}">${yliEsc(q.headerTitle.slice(0,28))}${q.headerTitle.length>28?"…":""}</span>`:"";
  const qtext=q.text?`<div class="qtext">${yliEsc(q.text).replace(/\\n/g,"<br>")}</div>`:`<p class="quiz-hint" style="margin-bottom:14px">Στο αρχείο αυτή η ερώτηση δεν έχει ξεχωριστό κείμενο· δες τις τέσσερις επιλογές.</p>`;
  const optHtml=answered?opts.map((o,i)=>{
    let cls="opt dis";
    if(i===correctIdx)cls+=" ok";
    else if(i===prev.i)cls+=" ko";
    return `<button type="button" class="${cls}">${yliEsc(o)}</button>`;
  }).join(""):opts.map((o,i)=>`<button type="button" class="opt" onclick="yliAnsPick(${i})">${yliEsc(o)}</button>`).join("");
  const fb=answered?`<div class="fbbox ${prev.ok?"":"ko"}" style="display:block">${yliFeedbackHtml(prev.ok,q,prev.i)}</div>`:`<div class="fbbox" id="${id.fb}"></div>`;
  area.innerHTML=`<div class="qcard">
    <div class="qmeta qmeta-row-split">
      <div class="qmeta-main">${sheetTag}${chapTag}${yliIdBadge}${headTag}</div>
      <div class="qmeta-tts-inline"></div>
    </div>
    <div class="qtag">Ερώτηση ${ctx.idx+1} από ${ctx.list.length} (σειρά αρχείου)</div>
    ${qtext}
    <div class="opts">${optHtml}</div>
    ${fb}
  </div>`;
  prevBtn.style.display=ctx.idx>0?"inline-block":"none";
  nextBtn.style.display=answered?"inline-block":"none";
}

function yliAnsPick(i){"""

    yli_render_new = """  const q=ctx.list[ctx.idx];
  const ansText=correctAnswerText(q)||"—";
  if(!ctx.ans[ctx.idx])ctx.ans[ctx.idx]={i:0,correctIdx:0,ok:true};
  fill.style.width=Math.round(ctx.idx/ctx.list.length*100)+"%";
  lbl.textContent=(ctx.idx+1)+"/"+ctx.list.length;
  const sheetTag=q.sheetName?`<span class="qmetatag">${yliEsc(q.sheetName)}</span>`:"";
  const chapTag=q.chapter?`<span class="qmetatag" title="${yliEsc(q.topic||q.chapter)}">${yliEsc(q.chapter)}</span>`:"";
  const yliJsonKey=q.id!=null&&String(q.id).length?"id":"n";
  const yliJsonVal=q.id!=null&&String(q.id).length?q.id:q.n;
  const yliIdBadge=yliJsonVal!=null&&String(yliJsonVal).length?`<span class="qjsonid" title="${yliEsc(yliJsonKey==="id"?"Αναγνωριστικό id στο JSON αυτού του αρχείου":"Αριθμός n (σειρά ερώτησης) στο JSON αυτού του αρχείου")}">${yliEsc(String(yliJsonVal))}</span>`:"";
  const headTag=q.headerTitle?`<span class="qmetatag" title="${yliEsc(q.headerTitle)}">${yliEsc(q.headerTitle.slice(0,28))}${q.headerTitle.length>28?"…":""}</span>`:"";
  const qtext=q.text?`<div class="qtext">${yliEsc(q.text).replace(/\\n/g,"<br>")}</div>`:`<p class="quiz-hint" style="margin-bottom:14px">Στο αρχείο αυτή η ερώτηση δεν έχει ξεχωριστό κείμενο.</p>`;
  const ansBlock=`<div class="ans-only seen">${yliEsc(ansText)}</div>`;
  area.innerHTML=`<div class="qcard">
    <div class="qmeta qmeta-row-split">
      <div class="qmeta-main">${sheetTag}${chapTag}${yliIdBadge}${headTag}</div>
      <div class="qmeta-tts-inline"></div>
    </div>
    <div class="qtag">Ερώτηση ${ctx.idx+1} από ${ctx.list.length} (σειρά αρχείου)</div>
    ${qtext}
    <div class="slbl" style="margin-top:12px;margin-bottom:8px">Σωστή απάντηση</div>
    ${ansBlock}
  </div>`;
  prevBtn.style.display=ctx.idx>0?"inline-block":"none";
  nextBtn.style.display="inline-block";
}"""

    if yli_render_block not in text:
        raise SystemExit("renderYliQ block not found")
    text = text.replace(yli_render_block, yli_render_new)

    text = text.replace(
        "function yliAnsPick(i){\n"
        "  const ctx=yliAct;\n"
        "  if(ctx.ans[ctx.idx])return;\n"
        "  const q=ctx.list[ctx.idx];\n"
        "  const order=yliOptOrder(q,ctx.idx);\n"
        "  const correctIdx=order.indexOf(q.correct);\n"
        "  const ok=i===correctIdx;\n"
        "  ctx.ans[ctx.idx]={i,correctIdx,ok};\n"
        "  const btns=document.querySelectorAll(\"#\"+ctx.ids.area+\" .opt\");\n"
        "  btns.forEach(o=>o.classList.add(\"dis\"));\n"
        "  if(correctIdx>=0&&correctIdx<btns.length)btns[correctIdx].classList.add(\"ok\");\n"
        "  if(!ok&&i>=0&&i<btns.length)btns[i].classList.add(\"ko\");\n"
        "  const fb=document.getElementById(ctx.ids.fb);\n"
        "  if(fb){\n"
        "    fb.style.display=\"block\";\n"
        "    fb.classList.toggle(\"ko\",!ok);\n"
        "    fb.innerHTML=yliFeedbackHtml(ok,q,i);\n"
        "  }\n"
        "  document.getElementById(ctx.ids.navPrev).style.display=ctx.idx>0?\"inline-block\":\"none\";\n"
        "  document.getElementById(ctx.ids.navNext).style.display=\"inline-block\";\n"
        "}\n\n",
        "",
    )

    text = text.replace(
        "      if(ctx._mesShuffledQ)bits.push(\"Η σειρά ερωτήσεων ανακατεύτηκε\");\n"
        "      if(ctx.shuffleAns)bits.push(\"Η σειρά των απαντήσεων ανακατεύτηκε ανά ερώτηση\");\n"
        "      sub+=bits.length?\". \"+bits.join(\" · \")+\".\":\". Η σειρά ερωτήσεων και των επιλογών ακολουθεί το αρχείο.\";\n",
        "      if(ctx._mesShuffledQ)bits.push(\"Η σειρά ερωτήσεων ανακατεύτηκε\");\n"
        "      sub+=bits.length?\". \"+bits.join(\" · \")+\".\":\". Η σειρά ερωτήσεων ακολουθεί το αρχείο.\";\n",
    )

    # Χωρίς κουμπί «Θεωρία Ενότητας» / theoria
    ti = text.find("let theoryJsonCache=null,theoryJsonPromise=null;")
    tj = text.find("function ulSolModalBackdropClick(ev){", ti if ti >= 0 else 0)
    if ti >= 0 and tj > ti:
        text = text[:ti] + text[tj:]

    OUT.write_text(text, encoding="utf-8")
    print("Έγραψε:", OUT)

    # Συγχρονισμός δεδομένων από AE007 (ή ρίζα)
    root = AE006.parent
    theoria_dst = AE006 / "theoria"
    if theoria_dst.exists():
        shutil.rmtree(theoria_dst)
        print("Αφαιρέθηκε:", theoria_dst)

    for name, src in (
        ("questions_bank.json", AE007 / "questions_bank.json"),
        ("insurance_agent_yli", AE007 / "insurance_agent_yli"),
    ):
        dst = AE006 / name
        if not src.exists():
            alt = root / name
            src = alt if alt.exists() else src
        if src.is_file():
            shutil.copy2(src, dst)
            print("Αντίγραφο:", dst)
        elif src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            print("Αντίγραφο:", dst)


if __name__ == "__main__":
    main()
