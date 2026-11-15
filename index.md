---
layout: default
title: 만든 페이지들
---

<script>document.documentElement.classList.add('js');</script>

{% assign total = 0 %}
{% for category in site.data.sites %}
  {% assign total = total | plus: category.sites.size %}
{% endfor %}

<div class="hero">
  <div class="hero-copy">
    <h1>만든 페이지들</h1>
    <p class="lede">GitHub Pages로 하나씩 만들어 온 사이트 {{ total }}개를 한곳에 모았습니다. 카테고리를 골라 둘러보거나, 아래에서 이름·설명·태그로 검색해 보세요.</p>
  </div>

  <nav class="toc" aria-label="카테고리별로 보기">
  {% for category in site.data.sites %}
    <a class="toc-item" href="#{{ category.id }}" style="--cat: {{ category.color }}">
      <span class="toc-dot" aria-hidden="true"></span>
      <span class="toc-name">{{ category.name }}</span>
      <span class="toc-count">{{ category.sites.size }}</span>
    </a>
  {% endfor %}
  </nav>
</div>

<div id="toolbar-sentinel" class="toolbar-sentinel" aria-hidden="true"></div>
<div class="toolbar">
  <div class="search">
    <input id="site-filter" type="search" placeholder="사이트 검색 — 이름, 설명, 태그" aria-label="사이트 검색" autocomplete="off">
    <kbd aria-hidden="true">/</kbd>
  </div>
  <span id="filter-count" class="filter-count" aria-live="polite"></span>
</div>

<p id="empty-state" class="empty-state" hidden>검색 결과가 없습니다. 다른 키워드로 찾아보세요.</p>

{% for category in site.data.sites %}
<section class="category" id="{{ category.id }}" style="--cat: {{ category.color }}">
  <h2>{{ category.name }} <span class="count">{{ category.sites.size }}</span></h2>
  <p class="section-desc">{{ category.description }}</p>

  <div class="cards">
  {% for site in category.sites %}
    <a class="card" href="{{ site.url }}" target="_blank" rel="noopener" data-search="{{ site.name }} {{ site.desc }} {{ site.tag }}" style="--i: {{ forloop.index0 }}">
      <span class="card-head">
        <span class="card-name">{{ site.name }}</span>
        <span class="card-arrow" aria-hidden="true">
          <svg viewBox="0 0 12 12" width="11" height="11" fill="none">
            <path d="M3 9L9 3M4.2 3H9v4.8" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </span>
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
