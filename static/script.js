$(document).ready(function() {

    const BASE_URL = "http://127.0.0.1:5000"

    const delete_user = $("#delete-usr");
    const confirm_delete = $("#confirm-delete-usr");
    const cancel_delete = $("#cancel-delete");

    delete_user.on("click", function() { // show confirmation box
        $("div.confirm-delete").removeClass("hidden");
    });

    cancel_delete.on("click", function() { // hide confirmation box
        $("div.confirm-delete").addClass("hidden");
    });

    async function sendDeleteRequest() {
        try {
            const request = await axios.post(`${BASE_URL}/users/delete`);

        } catch (err) {
            console.err("sendDeleteRequest function failed: ", err);
        }
        console.log("User successfully deleted.");
    }

    confirm_delete.on("click", function(e) {
        e.preventDefault();
        sendDeleteRequest();
    });

    // const options = {
    //     method: 'POST',
    //     url: 'https://quotel-quotes.p.rapidapi.com/quotes/qod',
    //     headers: {
    //       'content-type': 'application/json',
    //       'X-RapidAPI-Key': 'ce897d0754msh4c33bd40d7a0810p106de7jsn0f74d5e06259',
    //       'X-RapidAPI-Host': 'quotel-quotes.p.rapidapi.com'
    //     },
    //     data: {topicId: 100}
    // };

});
