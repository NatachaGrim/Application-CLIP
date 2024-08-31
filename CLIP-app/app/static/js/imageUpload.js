document.getElementById('image-upload-form').addEventListener('submit', function(event) {
    event.preventDefault();

    var formData = new FormData();
    var imageFile = document.getElementById('image-upload').files[0];
    formData.append('image', imageFile);

    fetch('/upload-image', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        var resultsGrid = document.getElementById('similar-images-grid');
        resultsGrid.innerHTML = ''; // Clear previous results

        data.similar_images.forEach(imagePath => {
            var div = document.createElement('div');
            div.className = 'grid-item';
            var img = document.createElement('img');
            img.src = imagePath;
            img.width = 200;
            div.appendChild(img);
            resultsGrid.appendChild(div);
        });

        var msnry = new Masonry(resultsGrid, {itemSelector: '.grid-item', percentPosition: true});
        imagesLoaded(resultsGrid).on('progress', function() {
            msnry.layout();
        });

        // Redirect to img_query.html (optional)
        // window.location.href = '/img_query';
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

function previewImage(event) {
    var reader = new FileReader();
    reader.onload = function() {
        var output = document.getElementById('image-preview');
        output.innerHTML = '<img src="' + reader.result + '" alt="Image preview">';
    };
    reader.readAsDataURL(event.target.files[0]);
}
