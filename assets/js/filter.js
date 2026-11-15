(function () {
  var input = document.getElementById("site-filter");
  var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
  var sections = Array.prototype.slice.call(document.querySelectorAll(".category"));
  var counter = document.getElementById("filter-count");
  var empty = document.getElementById("empty-state");
  var total = cards.length;

  // 스크롤로 툴바가 상단에 붙으면 배경을 깔아 줍니다.
  var toolbar = document.querySelector(".toolbar");
  var sentinel = document.getElementById("toolbar-sentinel");
  if (toolbar && sentinel && "IntersectionObserver" in window) {
    new IntersectionObserver(
      function (entries) {
        toolbar.classList.toggle("is-stuck", !entries[0].isIntersecting);
      },
      { rootMargin: "-4px 0px 0px 0px", threshold: 0 }
    ).observe(sentinel);
  }

  // 카드가 화면에 들어올 때 한 번만 나타납니다.
  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }
    );
    cards.forEach(function (card) {
      observer.observe(card);
    });
  } else {
    cards.forEach(function (card) {
      card.classList.add("is-visible");
    });
  }

  function apply() {
    if (!input) return;

    var query = input.value.trim().toLowerCase();
    var shown = 0;

    cards.forEach(function (card) {
      var haystack = (card.getAttribute("data-search") || "").toLowerCase();
      var match = !query || haystack.indexOf(query) !== -1;
      card.hidden = !match;
      if (match) shown += 1;
    });

    sections.forEach(function (section) {
      var visible = section.querySelectorAll(".card:not([hidden])").length > 0;
      section.hidden = !visible;
    });

    if (empty) empty.hidden = shown !== 0;
    if (counter) {
      counter.textContent = query
        ? shown + " / " + total + "개 표시"
        : total + "개 사이트";
    }
  }

  if (input) {
    input.addEventListener("input", apply);
    apply();
  }

  function isTyping(element) {
    if (!element) return false;
    return (
      element.tagName === "INPUT" ||
      element.tagName === "TEXTAREA" ||
      element.isContentEditable
    );
  }

  document.addEventListener("keydown", function (event) {
    if (!input) return;

    if (event.key === "/" && !isTyping(event.target)) {
      event.preventDefault();
      input.focus();
      return;
    }

    if (event.key === "Escape" && document.activeElement === input) {
      input.value = "";
      apply();
      input.blur();
    }
  });
})();
