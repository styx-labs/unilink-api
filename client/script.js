document.getElementById('githubForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const url = document.getElementById('githubInput').value;
    // https://unilink-api-zzkox64kyq-uk.a.run.app
    fetch('http://127.0.0.1:8000/rate_github', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'accept': 'application/json',
        },
        body: JSON.stringify({ github_url: url }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('githubResponse').textContent = `${JSON.stringify(data)}`;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('result').textContent = 'Error occurred while calling the API.';
    });
});

document.getElementById('portfolioForm').addEventListener('submit', function(event) {
    event.preventDefault();
    const url = document.getElementById('portfolioInput').value;
    // https://unilink-api-zzkox64kyq-uk.a.run.app
    fetch('http://127.0.0.1:8000/rate_portfolio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'accept': 'application/json',
        },
        body: JSON.stringify({ portfolio_url: url }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('portfolioResponse').textContent = `${JSON.stringify(data)}`;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('result').textContent = 'Error occurred while calling the API.';
    });
});