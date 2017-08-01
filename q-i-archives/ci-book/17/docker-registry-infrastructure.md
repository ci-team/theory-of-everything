---
slug: 17/docker-registry-infrastructure
title: Docker Registry Infrastructure
author: bookwar
date: 2017-08-01 12:19:48
tags: docker registry,infrastructure
categories: CI Book
link: https://quantum-integration.org/topic/17/docker-registry-infrastructure
---

Once you get exposed to the Cloud, DevOps and Everything As A Service world, you realize that almost every piece of software you might need has already been written by someone (or provided as a service). Why is not it all rainbows and unicorns then?

Because you do not need a tool, a software or a service. You need an _infrastructure_. 

## Start with the right problem
The most common issue in dealing with the infrastructure setup is that you keep forgetting about the task.

Of course it was hanging somewhere in the beginning, when you gathered the initial list of tools, which might be worth looking at. But then, once you get your hands on the list, you ask yourself:

*Which one is better - DockerHub, Quay, Artifactory or Nexus?*

And you are doomed.

As soon as you ask that question, you start to look into feature lists and marketing materials for the mentioned products. And then you build your entire choice strategy on figuring out how to get more by paying less.

The truth is: you do not need _more_. Usually you need just right amount of stuff to do the right task. And you can not replace one feature with five others you have got on a summer sale.

So let's do our homework first and get back to the task.

### The task
Again, we start with the question:

*We need a Docker Registry, how do we get one?*

And again, we are wrong.

No one needs a Docker Registry for the sake of having a Docker Registry alone. It is an implementation detail we have slipped in our problem statement. So let's remove it and find out what we are truly looking for:

**the infrastructure to build, store and distribute Docker images**

Now this is something to talk about.

### Build
Docker images are widely known as a delivery mechanism. And every delivery can work in two ways: it might be you who packages and delivers the software to the customer (or target environment), or it might be some third-party which packages the software and delivers it to you.

In the latter case you might get out just fine without the need to build a single Docker image on your own. So you can skip this part and focus on storing and distributing. Even better, you may forget about Docker images. Treat them as any external binary artifact: [download the tarball](https://docs.docker.com/engine/reference/commandline/save/), install, backup and watch for the updates.

If building Docker images is your thing, then welcome to the club and keep reading.

### Store
Let's say you use Docker images for packaging the apps to deploy them to production environment. You have Dockerfiles stored in your source code and CI/CD pipelines set to build them in your build service. And your release schedule is close to one release per hour.

With that kind of setup your Docker infrastructure is, in fact, stateless. If by some reason you lose all the Docker images currently available, you can rebuild them one by one directly from sources. Then you do not really need the storage function and can focus on building and distributing.

If, on the other hand, you need a long-term storage for Docker images, for example those which you have released and delivered to your customers, things get slightly more complicated.

In real life you are most likely to need both: there are base images you update once per year, there are images which you can not rebuild at all (there _shouldn't be_, but there usually _are_) and there are images which you build daily in hundreds.

And it totally makes sense to manage them differently. Maybe with different tools?

### Distribute

In the end it all comes to the distributing of images to the target environments. And target environment could be a developer workstation, CI system, production or customer environment. And these environments are usually distributed all over the globe.

Now Docker registry should connect to all three by the closest distance possible. Can you find a place for it? I guess not. And here is where caching, mirroring and proxying are brought into play.

With all that in mind, the natural question to ask is: how many registries you actually need? It appears, more than one.

## Build, store and distribute, shaken, not stirred

Let set up the context and consider the following situation: we develop an application, package it into container images, and then deploy them to several remote production environments (for example `eu` and `us`).

### Registries and their users

Users working within the infrastructure can be divided into three groups: contributors (**Dev**), build and test systems (**CI**), and the customer or consumer (**Prod**).

Dev users create and share random containers all day long. They do not have rules and restrictions. Dev containers should never go anywhere but the workstations and temporary custom environments. These containers are generally disposable and do not need a long-term storage.

CI users are automated and reliable, thus they can follow strict rules on naming, tagging and metadata.  Similarly to Dev, CI users generate and exchange huge amounts of disposable images. But as CI provides the data to make decisions (be it decision to approve a pull-request or decision to release the product), CI images must be verifiable and authoritative.

Prod users do not create containers, they work in a read-only mode and must have a strict policy on what is provided to them. The prod traffic is much lower in terms of variety of images consumed, while it might be high in terms of the amount of data fetched.

We could have tried to implement these use cases in one Docker registry: set up the naming rules, configure user and group permissions, enforce strict policy to add new repository, enable per-repository cleanup strategies.. But unless you invest huge amount of time in setting up the workflows, it is going to be complex and error-prone. It is also going to be fragile and hard to maintain. Simply imagine the update of a service which blocks your entire infrastructure.

The other way to do it is to setup several registries with separate scopes, concerns and SLA's.

Dev users get the **Sandbox** registry: no rules, free access, easy to setup, easy to clean, easy to redeploy.

CI users get the **CI Pool** registry: high traffic, readable by everyone, writable by CI only. It should be located close to the CI workers as it is going to be heavily used by CI builds and test runs.

There should be also **Prod** registry: only CI users can publish to it via *promotion* pipeline. This is the registry which you need to "export" to remote locations. It is also the registry you probably want to backup.

Depending on your workflows, you might also want to split the CI Pool registry into **CI Tests** and **CI Snapshots**. CI Tests would be used for images you build in pre-merge checks and in the test runs, while CI Snaphots are going to be the latest snapshot builds for each of the applications you develop, working or not.

In the following example of the infrastructure layout we've added also the remote **Archive** registry. Its primary purpose is to be a replica of certain important DockerHub images. It allows you to be flexible in keeping and overriding upstream images:

![0_1501591850558_docker registry infrastructure.png](/assets/uploads/files/1501591844554-docker-registry-infrastructure-resized.png)

### Tools

Finally, we come to that tool question again. But now we are equipped with the knowledge of how we want to use them.

We have high network throughput requirement for CI registries, thus we probably don't want to use a managed service priced by network usage. For random images in the Sandbox we do not want to pay for the number of repositories we create (in Docker, image name represents a repository). For caching instances we'd like to have an easy to maintain and easy to test open-source solution, which we can automate and scale. For archive we may want an independent remote registry with low network requirements but reliable storage options.

We now can choose and build the hybrid solution which is tailored for our needs, rather then go for the largest and most feature-reach service available and then unavoidably get into building up the pile of workarounds and integration connectors around it.


## Conclusion
It looks scary at first: you have just wanted a place to put the image and now you get multiple registries, scopes, network connections and interactions. But the truth is:  we have not *created* the additional complexity, we've *exposed* the layout, which has been there in your infrastructure from day one. Instead of hiding the complexity under the hood, we are making it explicit and visible. And by that we can design the infrastructure, which is effective and maintainable and solves the problem at hand, rather than uses those nice tools everyone is talking about.

