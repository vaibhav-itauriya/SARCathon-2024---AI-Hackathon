document.addEventListener('DOMContentLoaded', () => {
    const searchButton = document.getElementById('searchButton');
    const searchInput = document.getElementById('searchInput');
    const suggestions = document.getElementById('suggestions');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const results = document.getElementById('results');
    const historyDiv = document.getElementById('history');

    searchButton.addEventListener('click', () => {
        performSearch();
    });

    searchInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            performSearch();
        } else {
            getSuggestions(searchInput.value);
        }
    });

    async function performSearch() {
        const query = searchInput.value.trim();
        if (query === '') return;
        loadingSpinner.classList.remove('d-none');
        results.innerHTML = '';
        suggestions.innerHTML = '';
        try {
            const response = await fetch('/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query }),
            });
            const data = await response.json();
            loadingSpinner.classList.add('d-none');

            // Update results
            if (data.results.length > 0) {
                data.results.forEach(item => {
                    const card = document.createElement('div');
                    card.classList.add('card', 'mb-3');

                    const cardHeader = document.createElement('div');
                    cardHeader.classList.add('card-header');
                    cardHeader.textContent = item.question;

                    const cardBody = document.createElement('div');
                    cardBody.classList.add('card-body');

                    const cardText = document.createElement('p');
                    cardText.classList.add('card-text');
                    cardText.innerHTML = item.answer;

                    const feedbackDiv = document.createElement('div');
                    feedbackDiv.classList.add('mt-2');

                    const helpfulButton = document.createElement('button');
                    helpfulButton.classList.add('btn', 'btn-sm', 'btn-outline-success', 'me-2', 'feedback-button');
                    helpfulButton.textContent = 'Helpful';
                    helpfulButton.dataset.feedback = 'helpful';

                    const notHelpfulButton = document.createElement('button');
                    notHelpfulButton.classList.add('btn', 'btn-sm', 'btn-outline-danger', 'feedback-button');
                    notHelpfulButton.textContent = 'Not Helpful';
                    notHelpfulButton.dataset.feedback = 'not_helpful';

                    feedbackDiv.appendChild(helpfulButton);
                    feedbackDiv.appendChild(notHelpfulButton);

                    cardBody.appendChild(cardText);
                    cardBody.appendChild(feedbackDiv);

                    card.appendChild(cardHeader);
                    card.appendChild(cardBody);

                    results.appendChild(card);
                });
            } else {
                results.innerHTML = '<p>No relevant FAQs found.</p>';
            }

            // Update history
            if (data.history && data.history.length > 0) {
                historyDiv.innerHTML = '<h5>Your Recent Searches:</h5>';
                const historyList = document.createElement('ul');
                historyList.classList.add('list-group');
                data.history.slice().reverse().forEach(query => {
                    const listItem = document.createElement('li');
                    listItem.classList.add('list-group-item', 'history-item');
                    listItem.textContent = query;
                    historyList.appendChild(listItem);

                    // Make history items clickable
                    listItem.addEventListener('click', () => {
                        searchInput.value = query;
                        performSearch();
                    });
                });
                historyDiv.appendChild(historyList);
            }
        } catch (error) {
            loadingSpinner.classList.add('d-none');
            alert('An error occurred while fetching results.');
        }
    }

    async function getSuggestions(query) {
        if (query.trim() === '') {
            suggestions.innerHTML = '';
            return;
        }
        try {
            const response = await fetch('/suggestions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query }),
            });
            const data = await response.json();
            suggestions.innerHTML = '';
            data.forEach(item => {
                const suggestionItem = document.createElement('a');
                suggestionItem.href = '#';
                suggestionItem.classList.add('list-group-item', 'list-group-item-action', 'suggestion-item');
                suggestionItem.textContent = item;
                suggestions.appendChild(suggestionItem);
            });
        } catch (error) {
            // Handle error if needed
        }
    }

    suggestions.addEventListener('click', (event) => {
        if (event.target && event.target.classList.contains('suggestion-item')) {
            event.preventDefault();
            const text = event.target.textContent;
            searchInput.value = text;
            suggestions.innerHTML = '';
            performSearch();
        }
    });

    results.addEventListener('click', (event) => {
        if (event.target && event.target.classList.contains('feedback-button')) {
            const feedback = event.target.dataset.feedback;
            const question = event.target.closest('.card').querySelector('.card-header').textContent;
            // Send feedback to server
            fetch('/feedback', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: question, feedback: feedback }),
            });
            // Disable buttons and show thank you message
            const feedbackButtons = event.target.parentElement.querySelectorAll('.feedback-button');
            feedbackButtons.forEach(button => {
                button.disabled = true;
            });
            const thankYouMessage = document.createElement('p');
            thankYouMessage.classList.add('mt-2');
            thankYouMessage.textContent = 'Thank you for your feedback!';
            event.target.parentElement.appendChild(thankYouMessage);
        }
    });
});
