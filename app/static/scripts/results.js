$('.spotify.followers').on("click", (e) => {
   let artistBody = $(e.target).parent().parent();
   let player = artistBody.find(".spotify-player");
   toggleSpotifyPlayer(player);
});

function toggleSpotifyPlayer(playerObj) {
    if (playerObj.attr("data-active") == "true") {
       // Close player
       playerObj.removeClass("expanded");
       playerObj.attr("data-active", "false");
   } else {
       // Open player
       playerObj.addClass("expanded");
       playerObj.attr("data-active", "true");
   }
}

function shortenNumber(n) {
    if (n >= 1000000) return internationalize(n/1000000) + "M";
    if (n >= 1000) return internationalize(n/1000) + "K";
    return internationalize(n);
}
function internationalize(n) {
    return new Intl.NumberFormat().format(Math.round(n*10)/10);
}

$('.spotify.followers').each(function () {
    let followers = parseInt($(this).attr("data-followers"));
    $(this).append(shortenNumber(followers) + " followers");
});
