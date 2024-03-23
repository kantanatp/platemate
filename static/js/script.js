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
            let recipeList = document.getElementById('recipe-list');
            recipeList.innerHTML = '';
            data.recipes.forEach(recipe => {
                let listItem = document.createElement('li');
                listItem.textContent = recipe;
                recipeList.appendChild(listItem);
            });
            document.getElementById('results').style.display = 'block';
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});
