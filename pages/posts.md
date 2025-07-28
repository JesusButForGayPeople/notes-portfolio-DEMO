---
layout: page
title: Blog Posts
permalink: /posts/
---

<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ post.url }}">{{ post.title }}</a>
      <span>{{ post.date | date: "%A, %B %d, %Y" }}</span>
    </li>
  {% endfor %}
</ul>
