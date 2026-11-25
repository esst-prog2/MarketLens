# MarketLens: demo day script (1 December 2026, five minutes)

Slides: https://esst-prog2.github.io/MarketLens/slides/ (arrow keys or a clicker; `f` for full screen).
About 700 words, which is about five minutes at a calm pace. The main line comes back three times:
**"Real prices. No real money. And check the record before you trust a tip."**

Sources for every number: the slides' footers, `tests/test_promo_page.py` (checks 51, 18 and 2,871 on the slides),
PLANNING_LOG.md lines 60, 94 and 101.

---

## Before slide 1: the promise (0:00 to 0:20)

> In the next five minutes you'll see a place where a beginner can learn to invest
> with real market prices and without risking a single cent,
> and you'll learn one question that protects you from bad tips.

## Slide 1: For whom, and why (0:20 to 1:05)

> If you're new to investing, three things stop you.
> Where do I even start? Real money is an expensive teacher: your first mistakes cost you.
> And every tip you hear, from a friend, a video, an app, sounds sure: "this will go up."
> But was it ever right?
>
> MarketLens is for exactly that beginner. Look at this card from the app. It doesn't just say "Up".
> It says: of 61 earlier calls like this one, 60.7% were right. That's measured, not promised.
> Real prices. No real money. And the record comes with every call.

## Slide 2: The demo (1:05 to 2:20)

> This is a real run of the app, in four steps.
>
> One, learn: short guides on risk, on strategies like buy and hold or rebalancing.
> Save the ones you want for later.
> Two, choose a portfolio: three mixes of stocks, bonds and gold, each with its trade-off.
> Three, practise on real prices: you invest ten thousand virtual dollars and live through real market days,
> either past days, one click at a time, or today's prices, updated from Yahoo Finance while the app runs.
> Every day you see your portfolio move, and every forecast with its record.
> Four, see what happened: after 26 real trading days my Balanced portfolio was worth
> ten thousand three hundred ninety-four dollars. Nothing was generated and nothing was at risk:
> it is what that mix really did.
>
> It's free, it runs on your own computer, no account.

## Slide 3: Why you can trust it (2:20 to 3:20)

> A tool that teaches you to check tips has to pass the check itself. So MarketLens can't flatter itself.
>
> Every forecast is written down, with a timestamp, before the outcome exists, and it is never rewritten.
> Then it is compared with the simplest guess there is: "the market always goes up".
> Markets rise more often than they fall: from 2023 to 2026 that lazy guess was right 55% of the time.
> A tip is only worth something if it beats it.
>
> How do I know my code really does this? I broke it on purpose. Eighteen times.
> I planted eighteen bugs, and my 51 automated tests caught every single one.
>
> And my own model gets no favours: over 2,871 calls it is no better than "always up",
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

> Today you practise by choosing a portfolio and living with it. Next, and this is not built yet:
> can you beat it? You get a real past week, you make the call yourself, up or down,
> and MarketLens scores you with exactly the same rules as every model.
> You find out how good your gut really is.

## Closing slide (4:45 to 5:00)

> MarketLens. Real prices. No real money. And check the record before you trust a tip.
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
