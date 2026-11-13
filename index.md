---
title: Unify your data and AI platform
permalink: index.html
layout: home
---

## Lab exercises

Build grounded data agent solutions with Microsoft Fabric, Microsoft Foundry, and Microsoft Copilot Studio. These exercises support Microsoft skilling content on [Microsoft Learn](https://learn.microsoft.com/) and use Caldova Pharmaceuticals' launch-readiness challenges to connect business data, real-time operational intelligence, and AI agents.

Use the level 300 guided exercise to build an end-to-end solution, or take on the level 400 challenge to apply your skills to three customer solutions.

Before you begin, [prepare your environment]({{ '/Instructions/Labs/00-environment-setup.html' | relative_url }}) to confirm the required tools, licenses, permissions, and cloud services.

<hr>

{% assign labs = site.pages | where_exp:"page", "page.url contains '/Instructions/Labs'" %}
{% for activity in labs  %}
{% if activity.lab.title %}
### [{{ activity.lab.title }}]({{ site.github.url }}{{ activity.url }})


{% if activity.lab.level %}**Level**: {{activity.lab.level}} \| {% endif %}{% if activity.lab.duration %}**Duration**: {{activity.lab.duration}} minutes{% endif %}

{% if activity.lab.description %}
*{{activity.lab.description}}*
{% endif %}
<hr>
{% endif %}
{% endfor %}
