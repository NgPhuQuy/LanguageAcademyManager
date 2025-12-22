document.addEventListener("DOMContentLoaded", () => {

    /* ================= ANIMATION ================= */
    const items = document.querySelectorAll('.animate-up');
    if (items.length) {
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = 'running';
                }
            });
        }, { threshold: 0.2 });

        items.forEach(item => {
            item.style.animationPlayState = 'paused';
            observer.observe(item);
        });
    }

    /* ================= FILTER (FIX) ================= */
    const toggleFilter = document.getElementById("toggleFilter");
    const filterPanel = document.getElementById("filterPanel");

    if (toggleFilter && filterPanel) {
        toggleFilter.addEventListener("click", (e) => {
            e.stopPropagation();
            filterPanel.classList.toggle("show");
        });

        filterPanel.addEventListener("click", (e) => {
            e.stopPropagation();
        });

        document.addEventListener("click", () => {
            filterPanel.classList.remove("show");
        });
    }

    /* ================= THI THỬ ================= */
    window.loginBox = document.getElementById("loginBox");
    window.ageBox = document.getElementById("ageBox");
    window.testBox = document.getElementById("testBox");

    window.testTitle = document.getElementById("testTitle");
    window.answerBox = document.getElementById("answerBox");
    window.submitBtn = document.getElementById("submitBtn");
    window.resultBox = document.getElementById("resultBox");

    /* ================= NOTIFICATION (FIX) ================= */
    const notifyBtn = document.getElementById("notifyBtn");
    const notifyDropdown = document.getElementById("notifyDropdown");

    if (notifyBtn && notifyDropdown) {
        notifyBtn.addEventListener("click", (e) => {
            e.stopPropagation();
            notifyDropdown.classList.toggle("show");
        });

        notifyDropdown.addEventListener("click", (e) => {
            e.stopPropagation();
        });

        document.addEventListener("click", () => {
            notifyDropdown.classList.remove("show");
        });
    }

});



const minRange = document.getElementById('priceMin');
const maxRange = document.getElementById('priceMax');
const bubbleMin = document.getElementById('bubbleMin');
const bubbleMax = document.getElementById('bubbleMax');
const track = document.querySelector('.price-track');

/* Gắn bubble theo nút */
function setBubble(range, bubble) {
  const min = Number(range.min);
  const max = Number(range.max);
  const val = Number(range.value);

  const percent = ((val - min) / (max - min)) * 100;
  bubble.style.left = percent + '%';
  bubble.textContent = val.toLocaleString('vi-VN') + 'đ';
}

/* Đồng bộ 2 range + track */
function syncRanges() {
  let minVal = Number(minRange.value);
  let maxVal = Number(maxRange.value);

  /* Không cho min vượt max */
  if (minVal > maxVal) {
    minRange.value = maxVal;
    minVal = maxVal;
  }

  const minPercent = (minVal / minRange.max) * 100;
  const maxPercent = (maxVal / maxRange.max) * 100;

  /* Thanh xanh ở giữa */
  track.style.left = minPercent + '%';
  track.style.width = (maxPercent - minPercent) + '%';

  /* Bubble */
  setBubble(minRange, bubbleMin);
  setBubble(maxRange, bubbleMax);
}

/* Event */
minRange.addEventListener('input', syncRanges);
maxRange.addEventListener('input', syncRanges);

/* Init */
syncRanges();

document.addEventListener("DOMContentLoaded", () => {

  const filterCheckboxes = document.querySelectorAll(
    '.filter-language, .filter-level'
  );

  filterCheckboxes.forEach(cb => {
    cb.addEventListener('change', applyFilterInstant);
  });

  function applyFilterInstant() {
    const selectedLanguages = Array.from(
      document.querySelectorAll('.filter-language:checked')
    ).map(cb => cb.value);

    const selectedLevels = Array.from(
      document.querySelectorAll('.filter-level:checked')
    ).map(cb => cb.value);

    document.querySelectorAll('.course-item').forEach(card => {
      const cardLang = card.dataset.language;
      const cardLevel = card.dataset.level;

      const matchLang =
        selectedLanguages.length === 0 ||
        selectedLanguages.includes(cardLang);

      const matchLevel =
        selectedLevels.length === 0 ||
        selectedLevels.includes(cardLevel);

      card.style.display =
        (matchLang && matchLevel) ? '' : 'none';
    });
  }
});