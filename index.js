// Update Tahun Footer
document.getElementById('year').textContent = new Date().getFullYear();

// WhatsApp Integration
function kirimWA() {
  const nama = document.getElementById("nama").value;
  const pesan = document.getElementById("pesan").value;
  const email = document.getElementById("email").value;
  const nomor = "6281317768135";

  const textWA = `Halo Fahad, perkenalkan nama saya ${nama} (${email}).%0A%0A${pesan}`;
  
  const url = `https://wa.me/${nomor}?text=${textWA}`;
  
  window.open(url, "_blank");
}

// --- Algorithmic Nutrition Logic ---

// Activity Level Selection
const activityBtns = document.querySelectorAll('.activity-btn');
const activityInput = document.getElementById('activity_level');

activityBtns.forEach(btn => {
  btn.addEventListener('click', () => {
    // Reset all buttons
    activityBtns.forEach(b => {
      b.classList.remove('brutal-border-accent', 'bg-accent', 'text-zinc-950');
      b.classList.add('brutal-border');
    });
    
    // Set active button
    btn.classList.add('brutal-border-accent', 'bg-accent', 'text-zinc-950');
    btn.classList.remove('brutal-border');
    
    // Update hidden input
    activityInput.value = btn.dataset.value;
  });
});

// Form Submission
const nutritionForm = document.getElementById('nutrition-form');
const runBtn = document.getElementById('run-optimization');

nutritionForm.addEventListener('submit', (e) => {
  e.preventDefault();
  
  const payload = {
    weight: parseFloat(document.getElementById('weight').value),
    height: parseFloat(document.getElementById('height').value),
    age: parseInt(document.getElementById('age').value),
    gender: document.getElementById('gender').value,
    activity_level: activityInput.value
  };

  // Store payload in localStorage to pass to the results page
  localStorage.setItem('nutrition_payload', JSON.stringify(payload));
  
  // Redirect to results page
  window.location.href = 'nutriga_backend/static/results.html';
});

