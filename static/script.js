document.getElementById('lead-form').addEventListener('submit', function(e) {
    e.preventDefault();

    let userInput = document.getElementById('user_input').value;

    fetch('/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ user_input: userInput })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('generated_content').textContent = data.generated_content;
    })
    .catch(error => console.error('Error:', error));
});
