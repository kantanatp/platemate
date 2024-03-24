const dishImage = document.getElementById('dishImage');
const fileChosen = document.getElementById('file-chosen');
const nextButton = document.getElementById('nextButton');

dishImage.addEventListener('change', function() {
    fileChosen.textContent = this.files[0].name;
    nextButton.hidden = false; // Show the "Next" button once a file is selected
});
