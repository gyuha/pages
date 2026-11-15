(function () {
  var input = document.getElementById("site-filter");
  if (!input) return;

  var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
  var sections = Array.prototype.slice.call(document.querySelectorAll(".category"));
  var counter = document.getElementById("filter-count");
  var empty = document.getElementById("empty-state");
  var total = cards.length;

  function apply() {
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
      counter.textContent = query ? shown + " / " + total + "개 표시" : "";
    }
  }

  input.addEventListener("input", apply);
  apply();
})();
