---
slug: 12/what-is-ci
title: What is CI?
author: bookwar
date: 2017-06-26 09:21:58
tags: ci-book
categories: CI Book
link: https://quantum-integration.org/topic/12/what-is-ci
---

The Ultimate Source of Truth, Wikipedia, [defines](https://en.wikipedia.org/wiki/Continuous_integration) continuous integration as *the practice of merging all developer working copies to a shared mainline several times a day*.

My version goes a bit deeper:

**Definition:** *Continuous Integration (*CI*) is a practice of reaching the goal by doing small changes one at a time, while keeping the main artifact in a releasable state at all times.*

Why do I need a different definition? Let's take a closer look into it.

First of all, by this definition CI is not limited to the area of the programming or software development. Indeed, one can and should consider CI practice applied to any kind of *production* workflow:

Production starts with an *artifact*. It can be a software application, but it may as well be a book, or picture, or building. Artifact has a certain current state, for example, the concept of a book written on a napkin. And then there is a *goal* - the target state of an artifact we plan to reach (i.e. 450 pages in a hard cover).

Production *workflow* is the process of modifying the artifact, carrying it through the sequence of intermediate states to the predefined goal.

To add continuous integration to the picture we need a certain notion of quality: the way to differentiate the *releasable* state of an artifact from the unreleasable one. For a book we might say, for example, that book is in a releasable state if all its chapters are complete. The continuous integration of a book then would be printing the new chapter as soon as it is ready.

**Remark:** *As you may see the nature of continuous integration is actually quantum. As it follows from the definition, continuous integration is performed by applying small atomic changes - "quants". And all continuous integration workflows work with discrete chunks of data, rather than continuous streams.*

Another important note is that the above definition doesn't imply a specific implementation of the production workflow.

In the day to day conversations "doing CI" often means setting up a build service which runs certain tasks, build scripts and tests, triggered by certain events. But the CI concept itself does not require deployment automation, test coverage or Slack notifications of failed builds.

These technicalities are indeed useful and come naturally from applying the CI approach in software development, but these are helper methods, which should always be measured by and aligned to the generic idea.

In other words: while running automated tests is a good practice for implementing continuous integration development, continuous integration approach can not be reduced to just running automated tests.

The third thing I want to point out is that in the definition there is nothing said about some third-party, another actor, which you need to *integrate with*. There is a simple explanation for that: I believe that even when there is one and only acting entity in the workflow (one developer working on the codebase, one author writing the book..) there is still place for integration. Generally speaking, whenever you are involved in any kind of long-term process, you should treat "yourself today", "yourself yesterday" and "yourself tomorrow" as independently acting third-parties, which might work in parallel on different parts of the project and should exchange their work via documentation, code-review and comments just as the usual collaborators do.

