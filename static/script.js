$(document).ready(function() {

    const options = {
        method: 'POST',
        url: 'https://quotel-quotes.p.rapidapi.com/quotes/qod',
        headers: {
          'content-type': 'application/json',
          'X-RapidAPI-Key': 'ce897d0754msh4c33bd40d7a0810p106de7jsn0f74d5e06259',
          'X-RapidAPI-Host': 'quotel-quotes.p.rapidapi.com'
        },
        data: {topicId: 100}
    };

    async function getQuote(options) {
        try {
            const response = await axios.request(options);
            console.log(response.data);

            let newDiv = $("<div>"); // Create a new div element
            newDiv.append(`<h3>${response.data["quote"]}</h3>`);
            newDiv.append(`<h4>- ${response.data["name"]}</h4>`);
            
            return newDiv; // Return the entire div element

        } catch(error) {
            console.error(error);
        }
    }

    const quote_div = $("#quote-div");
    if (quote_div.length) {
        console.log("hello");
        getQuote(options).then((newDiv) => {
            quote_div.html(newDiv); // Set the HTML content of quote_div to the newDiv
        });
    }
});
