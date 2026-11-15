---
layout: default
title: 만든 페이지들
---

<div class="hero">
{% assign total = 0 %}
{% for category in site.data.sites %}
  {% assign total = total | plus: category.sites.size %}
{% endfor %}

<h1>만든 페이지들</h1>

<p class="lede">GitHub Pages로 하나씩 만들어 온 사이트를 한곳에 모았습니다. 카테고리를 골라 둘러보거나, 아래에서 이름·설명·태그로 검색해 보세요.</p>

<div class="stats">
  <span><strong>{{ total }}</strong>개의 사이트</span>
  <span><strong>{{ site.data.sites.size }}</strong>개의 카테고리</span>
  <span>GitHub Pages</span>
</div>

<nav class="jump" aria-label="카테고리 바로가기">
{% for category in site.data.sites %}
  <a href="#{{ category.id }}">{{ category.name }}</a>
{% endfor %}
</nav>
</div>

<div class="filter">
  <input id="site-filter" type="search" placeholder="사이트 검색 — 이름, 설명, 태그" aria-label="사이트 검색" autocomplete="off">
  <span id="filter-count" class="filter-count" aria-live="polite"></span>
</div>

<p id="empty-state" class="empty-state" hidden>검색 결과가 없습니다. 다른 키워드로 찾아보세요.</p>

{% for category in site.data.sites %}
<section class="category" id="{{ category.id }}">
  <h2>{{ category.name }} <span class="count">{{ category.sites.size }}</span></h2>
  <p class="section-desc">{{ category.description }}</p>

  <div class="cards">
  {% for site in category.sites %}
    <a class="card" href="{{ site.url }}" target="_blank" rel="noopener" data-search="{{ site.name }} {{ site.desc }} {{ site.tag }}">
      <span class="card-head">
        <span class="card-name">{{ site.name }}</span>
        <span class="card-arrow" aria-hidden="true">↗</span>
      </span>
      <span class="card-desc">{{ site.desc }}</span>
      <span class="card-foot">
        <span class="tag">{{ site.tag }}</span>
        <span class="card-host">{{ site.url | remove: 'https://' | remove: 'http://' | split: '/' | first }}</span>
      </span>
    </a>
  {% endfor %}
  </div>
</section>
{% endfor %}

<script src="{{ '/assets/js/filter.js' | relative_url }}"></script>
