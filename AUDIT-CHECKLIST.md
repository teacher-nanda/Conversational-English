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
15. Never narrate what the teacher will do on the page ("I click each card", "I write it down", "We write it in our notes"). Instructions only say what the student does or the question itself. The audit script checks this.
16. Homework must be creative and practice what the lesson taught, with DIFFERENT exercise types per slide (situations/choose, word order, read-and-write, personal plan, YouTube...). Never three unscramble slides in a row.
17. Deliver: copy to outputs, commit force:true, verify md5 on the Mac (re-commit if the first copy is stale).
18. Never open instructions with "Let's ..." (only the bare instruction). Adult tone, nothing childish.
19. Follow the book's exercise order; theory slide, then its practice, before the next topic.
20. Number badges (1, 2, 3) on answer options ONLY when the options are images/emojis. Word or sentence answers have no badges; the student just says the answer.
21. Beginner checkpoints/speaking drills: only language already taught; the scenario never tells the student what to say; a "Stuck? Click here for options" reveal is available. Drills reuse the lesson conversations with the student's own name.
22. Audio player sits in a small box on the instruction row, not at the bottom of the slide.
23. Never split ONE exercise over several slides ("(1/2)", "part 2"). Put all items on one slide; if it is long, the slide scrolls and the wordbank (and its audio) stays visible in a sticky box (class sticky-bank). audit_emp.py flags "(n/m)" titles; overflow is only allowed on slides with a sticky-bank.
24. Checkpoint scenarios: interesting, built only from what was taught so far (this lesson and earlier lessons, e.g. Welcome help phrases), never telling the student what to answer, with a "Stuck? Click here for options" help that lists only the needed phrases.
