function copyPath(path) {
    // Create a temporary input element
    var tempInput = document.createElement('input');
    document.body.appendChild(tempInput);
    tempInput.value = path;
    tempInput.select();
    document.execCommand('copy');
    document.body.removeChild(tempInput);

    // Change the text of the clicked div
    var divs = document.getElementsByClassName('bar_path');
    for (var i = 0; i < divs.length; i++) {
        if (divs[i].dataset.path === path) {
            var div = divs[i];
            div.classList.add('copied');
            div.innerHTML = '<b>&nbsp;Chemin copié ! (path copied!)</b>';

            // Revert the text back after 3 seconds
            setTimeout(function(div) {
                return function() {
                    div.classList.remove('copied');
                    div.innerHTML = '<b>&nbsp;Copier le chemin (copy path)</b>';
                };
            }(div), 3000);
            break;
        }
    }
}
