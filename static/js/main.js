document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    let formData = new FormData();
    formData.append('image', document.querySelector('input[type=file]').files[0]);
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.dish) {
            document.getElementById('dish-name').textContent = `Identified Dish: ${data.dish}`;
            let ingredientsSection = document.getElementById('ingredients-section');
            ingredientsSection.innerHTML = '';  // Clear previous entries

            if (data.ingredients_lists && data.ingredients_lists.length > 0) {
                data.ingredients_lists.forEach((item, index) => {
                    if (index >= 5) return;  // Limit to 5 recipes

                    let url = Object.keys(item)[0];
                    let ingredients = item[url];

                    let details = document.createElement('details');
                    let summary = document.createElement('summary');
                    summary.textContent = `Recipe ${index + 1}: ${new URL(url).hostname}`; // Displaying the hostname as the recipe source
                    details.appendChild(summary);

                    let list = document.createElement('ul');
                    ingredients.forEach(ingredient => {
                        let listItem = document.createElement('li');
                        listItem.textContent = ingredient;
                        list.appendChild(listItem);
                    });
                    details.appendChild(list);
                    ingredientsSection.appendChild(details);
                });
            } else {
                ingredientsSection.innerHTML = '<p>No ingredients found.</p>';
            }

            document.getElementById('results').style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});