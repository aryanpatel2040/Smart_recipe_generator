document.addEventListener('DOMContentLoaded', ()=>{
const tagButtons = document.querySelectorAll('.tag');
const ingInput = document.getElementById('ingredients-input');
tagButtons.forEach(b=>{
b.addEventListener('click', ()=>{
const val = b.textContent.trim();
let cur = ingInput.value.split(',').map(s=>s.trim()).filter(s=>s);
if(!cur.includes(val)) cur.push(val);
ingInput.value = cur.join(', ');
})
})


document.getElementById('find-btn').addEventListener('click', async ()=>{
const raw = ingInput.value;
const ingredients = raw.split(',').map(s=>s.trim()).filter(s=>s);
const match = document.querySelector('input[name="match"]:checked').value;
if(ingredients.length===0){ alert('Enter some ingredients'); return }
const res = await fetch('/find_recipes', {
method: 'POST', headers:{'Content-Type':'application/json'},
body: JSON.stringify({ingredients, match})
});
const data = await res.json();
const container = document.getElementById('results');
container.innerHTML = '';
if(data.error){ container.innerText = data.error; return }
if(data.recipes.length===0){ container.innerHTML = '<p>No recipes found</p>'; return }
data.recipes.forEach(r=>{
const div = document.createElement('div');
div.className = 'card';
div.innerHTML = `<h3>${r.title}${r.match_count?(' — '+r.match_count+' matched'):''}</h3>
<p><strong>Ingredients:</strong> ${r.ingredients.join(', ')}</p>
<p><strong>Steps:</strong> ${r.steps}</p>`;
container.appendChild(div);
})
})
})