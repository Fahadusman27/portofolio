/**
 * script.js
 * ---------
 * Handles form submission for the NutriGA diet recommender.
 * Sends a POST to /api/v1/recommend-diet and renders the JSON response.
 */

'use strict';

/* ──────────────────────────────────────────────────────────
   DOM references
────────────────────────────────────────────────────────── */
const form        = document.getElementById('profileForm');
const submitBtn   = document.getElementById('submitBtn');
const btnIcon     = document.getElementById('btnIcon');
const btnSpinner  = document.getElementById('btnSpinner');
const btnText     = document.getElementById('btnText');

const errorBanner  = document.getElementById('errorBanner');
const errorMessage = document.getElementById('errorMessage');
const resultsSection = document.getElementById('results');

/* ──────────────────────────────────────────────────────────
   Loading state helpers
────────────────────────────────────────────────────────── */
function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  btnIcon.classList.toggle('hidden', isLoading);
  btnSpinner.classList.toggle('hidden', !isLoading);
  btnText.textContent = isLoading ? 'Calculating best genes…' : 'Generate My Meal Plan';
}

/* ──────────────────────────────────────────────────────────
   Error display
────────────────────────────────────────────────────────── */
function showError(msg) {
  errorMessage.textContent = msg;
  errorBanner.classList.remove('hidden');
  resultsSection.classList.add('hidden');
  errorBanner.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function hideError() {
  errorBanner.classList.add('hidden');
}

/* ──────────────────────────────────────────────────────────
   Utility – round to 1 decimal
────────────────────────────────────────────────────────── */
const r1 = (n) => Math.round(n * 10) / 10;

/* ──────────────────────────────────────────────────────────
   Slot → badge CSS class
────────────────────────────────────────────────────────── */
const SLOT_CLASS = {
  breakfast: 'slot-breakfast',
  lunch:     'slot-lunch',
  dinner:    'slot-dinner',
  snack:     'slot-snack',
};

function slotClass(slot) {
  return SLOT_CLASS[slot?.toLowerCase()] ?? 'slot-snack';
}

/* ──────────────────────────────────────────────────────────
   Render – stat box (used in the calorie target row)
────────────────────────────────────────────────────────── */
function statBox(label, value, unit = '', accent = 'brand') {
  const accentMap = {
    brand:  ['text-brand-400',  'bg-brand-400/10'],
    purple: ['text-purple-400', 'bg-purple-400/10'],
    blue:   ['text-blue-400',   'bg-blue-400/10'],
    amber:  ['text-amber-400',  'bg-amber-400/10'],
  };
  const [textCls, bgCls] = accentMap[accent] ?? accentMap.brand;
  return `
    <div class="rounded-xl ${bgCls} p-4 flex flex-col gap-1">
      <span class="text-xs text-slate-500 font-medium">${label}</span>
      <span class="text-2xl font-extrabold ${textCls}">${value}<span class="text-sm font-medium ml-1 text-slate-400">${unit}</span></span>
    </div>`;
}

/* ──────────────────────────────────────────────────────────
   Render – macro pill
────────────────────────────────────────────────────────── */
function macroPill(label, value, unit, emoji) {
  return `
    <div class="macro-pill rounded-xl p-4 flex flex-col gap-1 cursor-default">
      <span class="text-lg">${emoji}</span>
      <span class="text-xs text-slate-500 font-medium">${label}</span>
      <span class="text-xl font-extrabold text-brand-400">${r1(value)}<span class="text-xs font-medium text-slate-400 ml-1">${unit}</span></span>
    </div>`;
}

/* ──────────────────────────────────────────────────────────
   Render – progress bar (actual vs target)
────────────────────────────────────────────────────────── */
function progressBar(label, actual, target, unit, color = '#22c55e') {
  const pct = Math.min(100, Math.round((actual / target) * 100));
  const overColor = pct >= 100 ? '#f87171' : color;
  return `
    <div>
      <div class="flex justify-between text-xs mb-1.5">
        <span class="text-slate-400 font-medium">${label}</span>
        <span class="text-slate-300">${r1(actual)} / ${r1(target)} ${unit} <span class="text-slate-500">(${pct}%)</span></span>
      </div>
      <div class="h-2 bg-slate-800 rounded-full overflow-hidden">
        <div class="h-full rounded-full progress-bar-fill" style="width: 0%; background: ${overColor};" data-width="${pct}%"></div>
      </div>
    </div>`;
}

/* ──────────────────────────────────────────────────────────
   Render – single food card
────────────────────────────────────────────────────────── */
function foodCard(item) {
  const slotLabel = item.meal_slot ?? 'Snack';
  const cls = slotClass(slotLabel);
  return `
    <div class="food-card rounded-2xl p-5 flex flex-col gap-4">
      <!-- Header -->
      <div class="flex items-start justify-between gap-3">
        <div>
          <span class="text-xs font-semibold px-2.5 py-1 rounded-full ${cls}">${slotLabel}</span>
          <h3 class="mt-2 text-base font-bold text-white leading-snug">${item.nama_bahan}</h3>
          <p class="text-xs text-slate-500 mt-0.5">Serving: ${r1(item.porsi_g)} g</p>
        </div>
        <div class="flex-shrink-0 text-right">
          <p class="text-2xl font-extrabold text-brand-400">${r1(item.kalori_kal)}</p>
          <p class="text-xs text-slate-500">kcal</p>
        </div>
      </div>

      <!-- Macro mini-bars -->
      <div class="grid grid-cols-3 gap-2 pt-2 border-t border-white/5">
        ${miniMacro('Protein', item.protein_g, '#a78bfa')}
        ${miniMacro('Carbs',   item.karbohidrat_g, '#60a5fa')}
        ${miniMacro('Fat',     item.lemak_g, '#fb923c')}
      </div>

      <!-- Fiber -->
      <p class="text-xs text-slate-500 -mt-1">
        🌾 Fiber: <span class="text-slate-400 font-medium">${r1(item.serat_g)} g</span>
      </p>
    </div>`;
}

function miniMacro(label, value, color) {
  return `
    <div class="flex flex-col items-center">
      <span class="text-base font-bold" style="color:${color}">${r1(value)}<span class="text-xs font-normal text-slate-500">g</span></span>
      <span class="text-[10px] text-slate-500">${label}</span>
    </div>`;
}

/* ──────────────────────────────────────────────────────────
   Render – GA stat chip
────────────────────────────────────────────────────────── */
function gaChip(label, value) {
  return `
    <div class="flex items-baseline gap-2">
      <span class="text-xs text-slate-500">${label}</span>
      <span class="text-sm font-semibold text-blue-300">${value}</span>
    </div>`;
}

/* ──────────────────────────────────────────────────────────
   Main render function
────────────────────────────────────────────────────────── */
function renderResults(data) {
  const { nutritional_targets: nt, total_macros: tm, meal_plan, ga_metadata: ga } = data;

  /* ①  Target stats */
  document.getElementById('targetStats').innerHTML =
    statBox('BMR',            r1(nt.bmr),            'kcal', 'blue')  +
    statBox('TDEE',           r1(nt.tdee),           'kcal', 'purple') +
    statBox('Target Calories', r1(nt.target_calories), 'kcal', 'brand')  +
    statBox('Deficit',        r1(nt.deficit_percentage), '%',   'amber');

  /* ②  Macro pills */
  document.getElementById('macroPills').innerHTML =
    macroPill('Total Calories', tm.total_calories, 'kcal', '🔥') +
    macroPill('Protein',        tm.total_protein_g, 'g',    '🥩') +
    macroPill('Carbs',          tm.total_carbs_g,   'g',    '🌾') +
    macroPill('Fat',            tm.total_fat_g,     'g',    '🥑');

  /* ②  Progress bars */
  document.getElementById('progressBars').innerHTML =
    progressBar('Calories', tm.total_calories, nt.target_calories, 'kcal', '#22c55e') +
    progressBar('Protein',  tm.total_protein_g, nt.target_protein_g, 'g',   '#a78bfa') +
    progressBar('Carbs',    tm.total_carbs_g,   nt.target_carbs_g,   'g',   '#60a5fa') +
    progressBar('Fat',      tm.total_fat_g,     nt.target_fat_g,     'g',   '#fb923c');

  /* ③  Food cards */
  document.getElementById('mealCards').innerHTML =
    (meal_plan ?? []).map(foodCard).join('');

  /* ④  GA diagnostics */
  document.getElementById('gaStats').innerHTML =
    gaChip('Generations',   ga.generations_run)    +
    gaChip('Population',    ga.population_size)    +
    gaChip('Best Fitness',  r1(ga.best_fitness_score));

  /* Show section */
  resultsSection.classList.remove('hidden');
  resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

  /* Animate progress bars after a tick so CSS transition fires */
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      document.querySelectorAll('.progress-bar-fill').forEach(el => {
        el.style.width = el.dataset.width;
      });
    });
  });
}

/* ──────────────────────────────────────────────────────────
   Form submit handler
────────────────────────────────────────────────────────── */
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  hideError();
  resultsSection.classList.add('hidden');

  /* Collect & coerce values */
  const payload = {
    age:            parseInt(form.age.value, 10),
    weight:         parseFloat(form.weight.value),
    height:         parseFloat(form.height.value),
    gender:         form.gender.value,
    activity_level: form.activity_level.value,
  };

  /* Basic client-side validation */
  if (!payload.gender || !payload.activity_level) {
    showError('Please select both Gender and Activity Level before continuing.');
    return;
  }
  if (isNaN(payload.age) || payload.age < 10 || payload.age > 19) {
    showError('Age must be between 10 and 19 years.');
    return;
  }
  if (isNaN(payload.weight) || payload.weight < 20 || payload.weight > 300) {
    showError('Weight must be between 20 kg and 300 kg.');
    return;
  }
  if (isNaN(payload.height) || payload.height < 100 || payload.height > 250) {
    showError('Height must be between 100 cm and 250 cm.');
    return;
  }

  setLoading(true);

try {
    const response = await fetch('/api/v1/recommend-diet', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });

    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
       const textError = await response.text();
       console.error("Vercel Error HTML:", textError);
       showError(`Server Vercel Error (${response.status}). Cek Log Vercel!`);
       return;
    }

    const json = await response.json();

    if (!response.ok) {
      /* FastAPI validation / server error */
      const detail = json?.detail;
      let msg = `Server error (${response.status})`;
      if (Array.isArray(detail)) {
        msg = detail.map(d => `${d.loc?.join(' → ') ?? 'field'}: ${d.msg}`).join('; ');
      } else if (typeof detail === 'string') {
        msg = detail;
      }
      showError(msg);
      return;
    }

    renderResults(json);

  } catch (err) {
    console.error(err);
    showError(
      'Could not reach the server. Make sure the FastAPI backend is running on port 8000.'
    );
  } finally {
    setLoading(false);
  }
});
