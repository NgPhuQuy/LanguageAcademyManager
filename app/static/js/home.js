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

    /* ================= FILTER ================= */

    const toggleBtn = document.getElementById('toggleFilter');
    const panel = document.getElementById('filterPanel');

    toggleBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      panel.classList.toggle('show');
    });

    document.addEventListener('click', () => {
      panel.classList.remove('show');
    });

    panel.addEventListener('click', (e) => {
      e.stopPropagation();
    });

    /* ================= THI THỬ ================= */
    window.loginBox = document.getElementById("loginBox");
    window.ageBox = document.getElementById("ageBox");
    window.testBox = document.getElementById("testBox");

    window.testTitle = document.getElementById("testTitle");
    window.answerBox = document.getElementById("answerBox");
    window.submitBtn = document.getElementById("submitBtn");
    window.resultBox = document.getElementById("resultBox");

});

/* ================= THI THỬ DATA ================= */

const questionBank = {
    english: [
        { q: "What ___ your name?", o: ["is", "are", "be"], a: 0 },
        { q: "She ___ to school.", o: ["go", "goes", "gone"], a: 1 },
        { q: "I have ___ apples.", o: ["some", "much", "any"], a: 0 },
        { q: "They ___ playing.", o: ["is", "are", "be"], a: 1 },
        { q: "My house is ___ than yours.", o: ["big", "bigger", "biggest"], a: 1 },
        { q: "He ___ a teacher.", o: ["am", "is", "are"], a: 1 },
        { q: "We ___ friends.", o: ["is", "are", "be"], a: 1 },
        { q: "She ___ coffee.", o: ["like", "likes", "liked"], a: 1 },
        { q: "This is ___ book.", o: ["a", "an", "the"], a: 0 },
        { q: "I ___ TV now.", o: ["watch", "am watching", "watched"], a: 1 }
    ],

    chinese: [
        { q: "你好 是 什么 意思？", o: ["Hello", "Goodbye", "Thanks"], a: 0 },
        { q: "我 ___ 学生", o: ["是", "有", "在"], a: 0 },
        { q: "你 ___ 哪里？", o: ["是", "去", "在"], a: 2 },
        { q: "谢谢 是 ___?", o: ["Sorry", "Thanks", "Hello"], a: 1 },
        { q: "中国 ___ 大", o: ["很", "也", "都"], a: 0 }
    ],

    korean: [
        { q: "안녕하세요 뜻은?", o: ["Xin chào", "Cảm ơn", "Tạm biệt"], a: 0 },
        { q: "저는 학생 ___", o: ["입니다", "있다", "하다"], a: 0 },
        { q: "감사합니다 là?", o: ["Xin lỗi", "Cảm ơn", "Xin chào"], a: 1 },
        { q: "한국 ___ 갑니다", o: ["에", "에서", "은"], a: 0 },
        { q: "이것은 ___ 책", o: ["제", "저", "이"], a: 0 }
    ],

    japanese: [
        { q: "こんにちは là?", o: ["Xin chào", "Tạm biệt", "Cảm ơn"], a: 0 },
        { q: "わたし ___ 学生です", o: ["は", "を", "に"], a: 0 },
        { q: "ありがとう nghĩa là?", o: ["Xin lỗi", "Cảm ơn", "Xin chào"], a: 1 },
        { q: "日本 ___ 行きます", o: ["へ", "で", "を"], a: 0 },
        { q: "これ ___ 本です", o: ["は", "に", "を"], a: 0 }
    ],

    french: [
        { q: "Bonjour nghĩa là?", o: ["Hello", "Bye", "Thanks"], a: 0 },
        { q: "Je ___ étudiant", o: ["suis", "es", "est"], a: 0 },
        { q: "Merci là?", o: ["Sorry", "Thanks", "Hello"], a: 1 },
        { q: "Il ___ professeur", o: ["suis", "est", "sont"], a: 1 },
        { q: "Nous ___ amis", o: ["sommes", "êtes", "sont"], a: 0 }
    ],

    german: [
        { q: "Hallo là?", o: ["Hello", "Bye", "Thanks"], a: 0 },
        { q: "Ich ___ Student", o: ["bin", "ist", "sind"], a: 0 },
        { q: "Danke là?", o: ["Sorry", "Thanks", "Hello"], a: 1 },
        { q: "Er ___ Lehrer", o: ["bin", "ist", "sind"], a: 1 },
        { q: "Wir ___ Freunde", o: ["bin", "ist", "sind"], a: 2 }
    ]
};

/* ================= THI THỬ LOGIC ================= */

let mode = "practice";
let currentQuestions = [];

function startPractice() {
    mode = "practice";
    startExam(10);
}

function startTest() {
    mode = "test";
    startExam(5);
}

function startExam(limit) {
    document.getElementById("ageBox")?.classList.add("d-none");
    document.getElementById("testBox")?.classList.remove("d-none");
    document.getElementById("submitBtn")?.classList.toggle("d-none", mode === "practice");

    const lang = document.getElementById("languageSelect")?.value;
    currentQuestions = questionBank[lang]?.slice(0, limit) || [];

    document.getElementById("testTitle").innerText =
        (mode === "practice" ? "📘 Luyện tập" : "📝 Thi thử") + " – " + lang.toUpperCase();

    renderQuestions();
}

function renderQuestions() {
    const questionContainer = document.getElementById("questionContainer");
    const resultBox = document.getElementById("resultBox");
    if (!questionContainer) return;

    questionContainer.innerHTML = "";
    resultBox?.classList.add("d-none");

    currentQuestions.forEach((q, i) => {
        questionContainer.innerHTML += `
            <div class="mb-4 question" data-answer="${q.a}">
                <h5>${i + 1}. ${q.q}</h5>
                ${q.o.map((opt, idx) => `
                    <label>
                        <input type="radio" name="q${i}"
                               value="${idx}"
                               onclick="checkAnswer(this)">
                        ${opt}
                    </label><br>
                `).join("")}
                <div class="text-success d-none mt-2 answer">
                    ✅ Đáp án đúng: <strong>${q.o[q.a]}</strong>
                </div>
            </div>
        `;
    });
}

function checkAnswer(input) {
    if (mode !== "practice") return;
    const box = input.closest(".question");
    if (input.value == box.dataset.answer) {
        box.querySelector(".answer").classList.remove("d-none");
    }
}

function submitTest() {
    let score = 0;
    document.querySelectorAll(".question").forEach(q => {
        const correct = q.dataset.answer;
        const checked = q.querySelector("input:checked");
        if (checked && checked.value == correct) score++;
    });

    const resultBox = document.getElementById("resultBox");
    resultBox.classList.remove("d-none");
    resultBox.innerHTML = `
        <h4>🎉 Hoàn thành</h4>
        <p>Bạn đúng <strong>${score}/${currentQuestions.length}</strong> câu</p>
    `;
}

/* ================= THÔNG BÁO (ĐÃ FIX LỖI) ================= */
const notifyBtn = document.getElementById("notifyBtn");
const notifyDropdown = document.getElementById("notifyDropdown");

if (notifyBtn && notifyDropdown) {
    notifyBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        notifyDropdown.classList.toggle("show");
    });

    document.addEventListener("click", () => {
        notifyDropdown.classList.remove("show");
    });
}

/*THỜI KHÓA BIỂU Á DÙNG COPY QUA CHO TEACHER CŨNG ĐC Á */


let currentWeek = 0;

const schedules = {
    0: [
        { day: "Thứ 2", subject: "English A2", time: "18:00 - 19:30", teacher: "Ms. Anna" },
        { day: "Thứ 4", subject: "English A2", time: "18:00 - 19:30", teacher: "Ms. Anna" },
        { day: "Thứ 6", subject: "Speaking Club", time: "19:00 - 20:00", teacher: "Mr. John" }
    ],
    "-1": [
        { day: "Thứ 3", subject: "Grammar A2", time: "18:00 - 19:30", teacher: "Ms. Anna" },
        { day: "Thứ 5", subject: "Listening A2", time: "18:00 - 19:30", teacher: "Ms. Anna" }
    ],
    "1": [
        { day: "Thứ 2", subject: "English B1", time: "18:00 - 19:30", teacher: "Mr. David" },
        { day: "Thứ 4", subject: "English B1", time: "18:00 - 19:30", teacher: "Mr. David" },
        { day: "Thứ 7", subject: "Mock Test", time: "09:00 - 10:30", teacher: "Center" }
    ]
};

function toggleSchedule() {
    const box = document.getElementById("scheduleBox");
    if (!box) return;

    box.classList.toggle("d-none");
    renderSchedule();
}

function renderSchedule() {
    const body = document.getElementById("scheduleBody");
    const title = document.getElementById("weekTitle");

    if (!body || !title) return;

    const data = schedules[currentWeek] || [];

    if (currentWeek === 0) title.innerText = "📅 Tuần hiện tại";
    else if (currentWeek > 0) title.innerText = "📅 Tuần sau";
    else title.innerText = "📅 Tuần trước";

    body.innerHTML = "";

    if (data.length === 0) {
        body.innerHTML = `
            <tr>
                <td colspan="4" class="text-muted py-4">
                    Không có lịch học
                </td>
            </tr>
        `;
        return;
    }

    data.forEach(item => {
        body.innerHTML += `
            <tr>
                <td>${item.day}</td>
                <td class="fw-semibold">${item.subject}</td>
                <td>${item.time}</td>
                <td>${item.teacher}</td>
            </tr>
        `;
    });
}

function prevWeek() {
    currentWeek--;
    renderSchedule();
}

function nextWeek() {
    currentWeek++;
    renderSchedule();
}


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
syncRanges();document.addEventListener("DOMContentLoaded", () => {

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
