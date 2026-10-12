/**
 * ==========================================================================
 * Fahad Usman Portfolio - Main Interaction Scripts
 * ==========================================================================
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Update Footer Year
  const yearEl = document.getElementById('year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // 2. Real-Time Jakarta (WIB) Clock
  function updateLiveClock() {
    const clockEl = document.getElementById('live-clock');
    if (!clockEl) return;
    const now = new Date();
    const timeString = now.toLocaleTimeString('id-ID', {
      timeZone: 'Asia/Jakarta',
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).replace(/\./g, ':');
    clockEl.textContent = `${timeString} WIB`;
  }
  setInterval(updateLiveClock, 1000);
  updateLiveClock();

  // 3. Stagger-In Animation via Intersection Observer
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
      }
    });
  }, { threshold: 0.08 });

  document.querySelectorAll('.stagger-in').forEach((el) => observer.observe(el));

  // 4. Mobile Navigation Menu with Accessible Keyboard Support
  const menuBtn = document.getElementById('mobile-menu-btn');
  const closeBtn = document.getElementById('close-menu-btn');
  const mobileMenu = document.getElementById('mobile-menu');

  function openMenu() {
    if (!mobileMenu) return;
    mobileMenu.classList.remove('translate-x-full');
    mobileMenu.classList.add('translate-x-0');
    if (menuBtn) menuBtn.setAttribute('aria-expanded', 'true');
    if (closeBtn) closeBtn.focus();
  }

  function closeMenu() {
    if (!mobileMenu) return;
    mobileMenu.classList.add('translate-x-full');
    mobileMenu.classList.remove('translate-x-0');
    if (menuBtn) menuBtn.setAttribute('aria-expanded', 'false');
    if (menuBtn) menuBtn.focus();
  }

  if (menuBtn) menuBtn.addEventListener('click', openMenu);
  if (closeBtn) closeBtn.addEventListener('click', closeMenu);

  if (mobileMenu) {
    mobileMenu.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', closeMenu);
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && mobileMenu && !mobileMenu.classList.contains('translate-x-full')) {
      closeMenu();
    }
  });

  // 5. NutriGA Activity Level Selector
  const activityBtns = document.querySelectorAll('.activity-btn');
  const activityInput = document.getElementById('activity_level');

  activityBtns.forEach((btn) => {
    btn.addEventListener('click', () => {
      activityBtns.forEach((b) => {
        b.classList.remove('brutal-box-accent', 'bg-accent', 'text-zinc-950');
        b.classList.add('brutal-box');
      });
      
      btn.classList.add('brutal-box-accent', 'bg-accent', 'text-zinc-950');
      btn.classList.remove('brutal-box');
      
      if (activityInput) {
        activityInput.value = btn.dataset.value;
      }
    });
  });

  // 6. NutriGA Form Submission with Loading & Validation States
  const nutritionForm = document.getElementById('nutrition-form');
  const runBtn = document.getElementById('run-optimization');
  const runBtnText = document.getElementById('run-btn-text');
  const formError = document.getElementById('form-error');

  if (nutritionForm) {
    nutritionForm.addEventListener('submit', (e) => {
      e.preventDefault();
      
      const weightVal = parseFloat(document.getElementById('weight')?.value);
      const heightVal = parseFloat(document.getElementById('height')?.value);
      const ageVal = parseInt(document.getElementById('age')?.value, 10);
      const genderVal = document.getElementById('gender')?.value || 'male';
      const activityVal = activityInput ? activityInput.value : 'moderate';

      if (isNaN(weightVal) || isNaN(heightVal) || isNaN(ageVal) || weightVal <= 0 || heightVal <= 0 || ageVal <= 0) {
        if (formError) {
          formError.classList.remove('hidden');
        }
        return;
      }

      if (formError) {
        formError.classList.add('hidden');
      }

      if (runBtnText) {
        runBtnText.textContent = "Computing Next Gen...";
      }
      if (runBtn) {
        runBtn.setAttribute("disabled", "true");
        runBtn.classList.add("opacity-75", "cursor-wait");
      }

      const payload = {
        weight: weightVal,
        height: heightVal,
        age: ageVal,
        gender: genderVal,
        activity_level: activityVal
      };

      localStorage.setItem('nutrition_payload', JSON.stringify(payload));
      
      setTimeout(() => {
        window.location.href = 'api/static/results.html';
      }, 250);
    });
  }
});

// 7. Global WhatsApp Transmission Handler (invoked by form onsubmit)
function kirimWA(event) {
  if (event && event.preventDefault) {
    event.preventDefault();
  }

  const namaEl = document.getElementById("nama");
  const emailEl = document.getElementById("email");
  const pesanEl = document.getElementById("pesan");
  const errorEl = document.getElementById("wa-error");

  const nama = (namaEl ? namaEl.value : "").trim();
  const email = (emailEl ? emailEl.value : "").trim();
  const pesan = (pesanEl ? pesanEl.value : "").trim();
  const nomor = "6281317768135";

  if (!nama || !pesan) {
    if (errorEl) {
      errorEl.classList.remove("hidden");
    }
    return;
  }

  if (errorEl) {
    errorEl.classList.add("hidden");
  }

  const senderInfo = email ? `${nama} (${email})` : nama;
  const textWA = encodeURIComponent(`Halo Fahad, perkenalkan nama saya ${senderInfo}.\n\n${pesan}`);
  const url = `https://wa.me/${nomor}?text=${textWA}`;
  
  window.open(url, "_blank", "noopener,noreferrer");
}
