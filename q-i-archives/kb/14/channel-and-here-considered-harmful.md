---
slug: 14/channel-and-here-considered-harmful
title: @channel and @here considered harmful
author: bookwar
date: 2017-06-29 15:54:30
tags: communication,slack
categories: Knowledge Base
link: https://quantum-integration.org/topic/14/channel-and-here-considered-harmful
---

Let's talk about Slack best practices. Or should I say worst practices?

In particular about **@channel** and **@here**

For those who don't know: the **@channel** in Slack alerts everyone on the chat and **@here** alerts everyone on the chat who is online. Both commands are widely used, but both are, in fact, harmful.

## The Problem

There is a team **A-Team** and a channel **#a-team-channel**. The audience of the channel is: 10 members from the A-Team itself, and 500 members of other teams who came to the channel to discuss the issue with the A-Team or just to browse what is going on there.

Now you come to the channel and want to get the attention of one of the A-Team members.

If you use **@channel** keyword you alert 510 people at once distracting them from what they are doing. If you use **@here** - you alert about 300 people, and maybe no one from the A-Team itself. And this is extremely counter-productive and leads to people disabling Slack notifications altogether.

## What are the alternatives?

Slack supports two more alerting mechanisms: keywords and groups.

### User Groups

[Groups](https://get.slack.help/hc/en-us/articles/212906697-User-Groups) provide the more formal way of managing groups casts.

**Pros:** You can create a group and add people to it. Group members themselves don't need to do anything on their side.

**Cons:** Group management requires admin rights, it is not flexible, and can not be self-managed. If you change your current role from duty engineer to the research engineer for a week, you can not simply leave the 'on-duty' group and must contact Slack admin to do that for you.

### Keywords

With [keywords](https://get.slack.help/hc/en-us/articles/201398467-Highlight-word-notifications) you can configure per-user alerts and set the notification if someone mentioned a specific word in chat. For example I have an alert set whenever someone mentions the word 'jenkins'.

But keywords can also be used in a more organized way. If A-Team chooses its personal keyword, like **a-team**, and every team member subscribes to it, then this keyword can be used instead of 'channel' and 'here' casts. It is going to be more direct and straight to those people you actually need.

**Pros:** Fully flexible. Team members decide and manage which keywords they care about.
**Cons:** Requires self-discipline. If you are the duty engineer, you must go and subscribe to "on-duty" keyword to get alerted.

### Critical remark

Note that the important step here is to promote the keyword or user group to the people outside of the team. It needs to be discoverable the same way as e-mail address or Jira project.

We found it the most effective when you add line "To contact A-Team use keyword 'a-team'" to the #a-team-channel topic.

## Benefits

The groups/keywords approach reduces fragmentation, as one don't need to create separate channels with smaller number of participants to limit the alerting power.

It increases the cross-team presence, as you can join more channels in a browsing mode, without increasing your alerts stream. You can watch and recap on what has happened in the A-Team channel during the day, even if you are not the direct responsible person and don't get alerted.

It improves the overall usage of Slack as alerts become more specific and go directly to the people you want to target.

## Example

Suppose we have a Datacenter Engineers and Office IT Engineers teams. Each team has its own responsibilities but they also share a lot of common knowledge.

The Classical Way says we create a #dc-team and #it-team channels. The typical dialog then looks as follows:

```txt
In #dc-team

  user: @here Server ABC is not responding, please check!!   # Alert includes ~50 server users
  dc-eng: logs?
  user: ..
  dc-eng: ask at #it-team

In #it-team:

  user: @here Can not reach server ABC, please check!!        # Alert includes ~100 office users
  user: dc-team send me here
  it-eng: logs?
  user: .. same logs again..
  it-eng: some more logs?
  user: ...
  it-eng: ask at #dc-team

And back to #dc-team..
```
In this case user has to repeat the entire context of the discussion again and again.

The Keyword Way says we should have just one channel, which is the #support channel. DC Engineers respond to the **dc-team** keyword, and Office IT Engineers to **it-team**.

The above dialog would look as follows:
```txt
In #support
  user: dc-team, server ABC is not responding, please check!!   # Alert ~5 people
  dc-eng: logs?
  user: ..
  dc-eng: it-team, ^^                                         # Alert ~7 people
  it-eng: some more logs?
  user: ...
  it-eng: @dc-eng ^^                                           # Alert 1 person, who is already participating
...
```
Here two team can be cast independently but share the context of the discussion. And channels can be aligned by topic, rather than by current team structure.

