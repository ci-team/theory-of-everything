
---
slug: 15/do-not-blame-the-ci
title: Do not blame the CI
author: bookwar
date: 1499878784257

tags: ci-book
categories: CI Book

link: https://quantum-integration.org/topic/15/do-not-blame-the-ci
---

In the [previous article](https://quantum-integration.org/topic/12/what-is-ci) I explained the underlying idea behind the Continuous Integration concept. Now let's get a bit more practical and talk about how this idea appears in software development.

## CI starts with the code

CI is a development practice. This is the official meaning of the term and you could find it all over the hardcore Software Architecture and DevOps conferences, in books and high-level discussions. Unfortunately it is rarely known as such among real world programmers, even though they make up the target audience of it.

Therefore, when introducing CI, the hardest obstacle you see is rarely technical (in the end any tech problem can be solved with the right amount of Python scripting). The true complexity comes from the understanding that **CI is not something for infrastructure team to automate, it is something for development team to follow**.

Let me elaborate.

### CI needs good code structure

The possibility to [merge changes into the mainline at least once per day](https://en.wikipedia.org/wiki/Continuous_integration) does not come for granted. If every change you do in the codebase has a footprint of 100500 files, the only thing you get at the end of the day is the pile of merge conflicts.

Tight coupling, huge files, mixed concerns and responsibilities.. everyone knows these are signs of a bad code quality. CI exposes them and makes them harder to avoid.

If you find that you bump into someone else's conflicting changes all the time, do not blame the CI, consider it to be a good reason to change the code structure.

### CI needs good discipline

CI practice assumes that you keep the mainline in a releasable state. Every time there is a concern about the current state of the codebase, one should stop doing anything else and deal with the issue.

No matter how it is important for you to merge your particular change, it must be delayed.

More to that, do not try to fix the issue in place adding more untested code on top of the broken state. Revert to the known working state and unblock others.

If *master is failing*, do not blame the CI, revert the change to previous known state and deal with the commit which introduces the regression separately.

### CI needs good communication

CI practice needs you to be able to work independently. One part of it is to reduce the footprint of your changes, the other is to make sure that you do not overlap with someone else's work .

You don't want to spent time writing that helper function just to find out that your colleague  has just merged it into master.

So when you find yourself implementing new feature on top of the functionality, which has been just removed by someone else's refactoring work, don't blame CI, but rather introduce the code and design review process and improve your communication channels.

### CI needs good management

CI practice requires you to merge unfinished functionality into the code. 

 * It saves the time spent on integration efforts as integration is done by small steps in a controlled way.
 * It helps to track the current progress of a feature implementation, as there is no unpredictable integration explosion waiting in the very end.
 * It also gives you the flexibility to release a product on time even if planned features were delayed or canceled.

The downside is that every unfinished feature introduces a technical debt. And once you've decided to cancel development for a certain subproject, you can not simply get out and move on to the new one. There is a cleanup you must perform.

If your code is full of deprecated feature toggles, do not blame the CI, but create the policy to track feature implementations and find time for regular cleanups.

## CI is not magic

 CI can not magically make your life easier, your development faster, your code better, your tests greener and your salary higher. It provides _you_ with tools to do that. 

So, generally, just stop blaming the CI :)

