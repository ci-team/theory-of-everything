---
slug: 10/layered-saltstack-environments
title: Layered Saltstack environments
author: bookwar
date: 1498240487794
tags: cfgmgmt,saltstack
categories: Knowledge Base
link: https://quantum-integration.org/topic/10/layered-saltstack-environments
---

Suppose there exists a certain repository of saltstack states and pillars, which you'd like to reuse. Let's call it *base repo*.

Forking or copy-pasting could be quite costly, especially in case when base repo is changing quite fast and you don't have any control of it. The better approach would be to refactor and isolate shared states and pillars (moving them to saltstack formulas and external key-value storage) but it is expensive and time-consuming as well.

Then there is a simple fallback option: overlaying salt configurations with the help of salt environments.

# Problem description

There are two sources of salt configurations: base and overlay. We have control over overlay repo and salt-master configuration.

The task is to use the base states and pillar data but ignore the base top file, using only the top files from overlay repo.

## Prerequisites
### Filesystem layout
Base and overlay code is checked out into different subfolders.
```
/srv/salt/
          base/
                states/
                        top.sls
                        base_state.sls
                        another_base_state.sls
                pillars/
                        top.sls
                        base_pillar.sls
                        another_base_pillar.sls
          overlay/
                states/
                        top.sls
                        overlay_state.sls
                pillars/
                        top.sls 
                        overlay_pillar.sls
```

### Salt master paths configuration
Base and overlay environments are configured to point to their code.
```yaml
file_roots:
  base:
    - /srv/salt/base/states
  overlay:
    - /srv/salt/overlay/states

pillar_roots:
  base:
    - /srv/salt/base/pillars
  overlay:
    - /srv/salt/overlay/pillars
    
env_order: ['base','overlay']
```

### /srv/salt/base/states/top.sls
In top.sls file of the base environment there are some incompatible wildcard mappings, which we'd like to avoid.
```yaml
base:
  '*':
    - base_state
    - another_base_state
```
### /srv/salt/base is read-only
We can not edit the *base* code as it is synced with the upstream repo which we don't control.

## Desired behaviour
Triggering *salt '\*' state.highstate* on a salt master should execute the *base_state* and *overlay_state*, but not *another_base_state*.

# Solution

1. Configure salt-master to use another name for the top-file. 

   In */etc/salt/master* specify:
   ```yaml
   state_top: overlay_top.sls
   ```
2. Create */srv/salt/overlay/states/overlay_top.sls*
   ```yaml
   base:
     '*':
       - base_state
   
   overlay:
     '*':
       - overlay_state
   ```
3. Same for pillars in */srv/salt/overlay/pillars/overlay_top.sls*

   ```yaml
   base:
     '*':
       - base_pillar
   
   overlay:
     '*':
       - overlay_pillar
   ```
With this setup the salt-master will read only the *overlay_top.sls*. It will ignore all top.sls files in the base environment, but still apply the *base*-section of the overlay_top file.

