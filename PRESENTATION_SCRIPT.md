# MarketLens: demo day script (1 December 2026, five minutes)

Slides: https://esst-prog2.github.io/MarketLens/slides/ (arrow keys or a clicker; `f` for full screen).
About 640 words, which is about five minutes at a calm pace. The main line comes back three times:
**"See the record before you trust the tip."**

Sources for every number: the slides' footers, `tests/test_promo_page.py` (checks 51, 18 and 2,871 on the slides),
PLANNING_LOG.md lines 60, 94 and 101.

---

## Before slide 1: the promise (0:00 to 0:20)

> In the next five minutes you'll learn one question that protects you from bad market tips,
> and you'll see a place where you can practise investing without risking a single cent.

## Slide 1: For whom, and why (0:20 to 1:10)

> If you're new to investing, you hear tips everywhere: a friend, a video, an app.
> "This will go up." Every one of them sounds sure.
> But almost none of them tell you the one thing that matters: how often were they right before?
>
> MarketLens is for beginners. Look at this card from the app. It doesn't just say "Up".
> It says: 61 earlier calls like this one, and 60.7% of them were right.
> The record comes with the call.
>
> So the problem is simple: beginners can't judge a tip, and learning with real money is expensive.
> MarketLens fixes both. See the record before you trust the tip.

## Slide 2: The demo (1:10 to 2:20)

> Here is a beginner's first week, from a real run of the app.
>
> One: you answer three short questions: what you want, what you know, how much up and down you can take.
> Two: you invest ten thousand dollars. Virtual money, in a Balanced plan.
> Three: you live through real market days, real prices from 2023, one day at a time.
> At every step the app shows its forecasts and their records.
> Four: after 26 trading days, you see what happened: ten thousand three hundred ninety-four dollars.
>
> You learned how a real portfolio moves, and nothing was at risk.
> It's free, it runs on your own computer, no account.

## Slide 3: Why you can trust it (2:20 to 3:20)

> A tool like this is only useful if it's honest. So MarketLens can't flatter itself.
>
> Every forecast is written down, with a timestamp, before the outcome exists, and it is never rewritten.
> Then it's scored on the same days as the simplest possible guess: "the market always goes up".
>
> How do I know my code really does that? I broke it on purpose. Eighteen times.
> I planted eighteen bugs, and my 51 automated tests caught every single one.
>
> And yes, my own model gets no favours either. Over 2,871 calls it is no better than "always up",
> and the app says exactly that.

## Slide 4: What I learned (3:20 to 4:10)

> That moment was the biggest lesson of this project.
> When my model didn't win, I was tempted to keep tweaking it until it did.
> But if you keep trying long enough, something will win, just by luck.
>
> So on the eleventh of October I wrote this decision into my planning log:
> MarketLens measures whether any model beats the baselines. It is not a model that has to beat them.
> The measurement became the product. Honest beats impressive.

## Slide 5: What's next (4:10 to 4:45)

> Next, and this is not built yet: can you beat it?
> You get a real past week, you make the call, up or down,
> and MarketLens scores you with exactly the same rules as every model.
> You find out how good your gut really is.

## Closing slide (4:45 to 5:00)

> MarketLens. See the record before you trust the tip.
> The link is on the screen. Thank you.

---

### Delivery notes

- Don't read the slides: they hold the pictures, you tell the story (the instructor's Session 10 advice).
- Pause after "how often were they right before?" (slide 1) and after "Eighteen times." (slide 3).
- If you run long, cut slide 2's last two lines first.
- Possible questions:
  - *"Why not on the phone?"* It's a local app; the page and the video work on a phone.
  - *"Is the model useless then?"* It's one contender. The point is that you can see that it doesn't beat the simplest guess.
  - *"Where do the prices come from?"* Free Yahoo Finance daily prices; the replay is a stored snapshot.
