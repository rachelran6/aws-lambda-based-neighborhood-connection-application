logout = (url) => {
    $.ajax({
        url: url, 
        type: "POST", 
        success: function(result) {
            if (result['isSuccess']) {
                window.location.replace(response["url"])
            }
    }});
}


markLocationOnMap = () => {
    
}