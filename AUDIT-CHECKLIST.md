# Empower lessons — Nanda's audit checklist (run on EVERY lesson before delivering)

Run: `python3 audit_emp.py <lesson index.html>` — it must print `AUDIT: OK`. Then look at the screenshots.

1. NEVER reduce font size. No `zoom`, no smaller inline font-size to make things fit. If it does not fit, split the slide or move things (e.g. audio player next to the instruction / wordbank).
2. Every new sentence goes on its own line (instructions, notes, dialogues, deck cards, answers).
3. Title sits right under the header dots — no wasted space at the top of the page.
4. Enough space between a wordbank and the questions (at least ~20px).
5. The teacher guides the live lesson: the student answers aloud (numbers 1, 2, 3 / letters a, b, c), never "Click…", "Write them here…". Homework slides are the only student-driven ones.
6. Instructions are friendly, not rude: "Let's…", questions ("Which words are I'm or we're?"). No bare orders like "Answer the questions about you."
7. Homework: never the same exercise as in class. If letters are scrambled, NO wordbank (it only gives the answer). Homework is self-contained, can use new vocabulary and spelling practice.
8. Options in exercises numbered (CSS numopts) so the student can say the number; vary the position of correct answers.
9. American English; 100% English; one-on-one wording (no pair/partner/class); no "Nanda" in activities ("me").
10. Only recorded book audio, never synthetic voices.
11. NEVER make an exercise with patterned answers (a, b, a, b / all the same / 1-2-3 in order) and NEVER put the answers in the same order as the wordbank (or reversed). Shuffle both the wordbank and the items. The audit script checks this.
12. NEVER show a wordbank AND scrambled letters on the same exercise. Typed-answer wordbanks: students can click a word to cross it out when used.
13. "Find it / match it" exercises: no hints (don't underline or mark the answers), don't make the student feel like a kid; show a small reference box (e.g. Short forms: We are – We're) and let the student search the text.
14. Instruction for a question slide is just the question + the answer line (e.g. "What other countries do you know in English?"); never narrate what the teacher will do ("I will write it down").
15. Deliver: copy to outputs, commit force:true, verify md5 on the Mac (re-commit if the first copy is stale).
