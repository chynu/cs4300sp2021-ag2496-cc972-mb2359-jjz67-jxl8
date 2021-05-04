$('.spotify.followers').on("click", (e) => {
    console.log("HELLO!");
   let artistBody = $(e.target).parent().parent();
   let player = artistBody.find(".spotify-player");
   if (player.attr("data-active") == "true") {
       // Close player
       player.removeClass("expanded");
       player.attr("data-active", "false");
   } else {
       // Open player
       player.addClass("expanded");
       player.attr("data-active", "true");
   }
});

function shortenNumber(n) {
    let s = "" + n;
    let suffix = "";
    let threes = Math.floor(s.length / 3);
    if (threes == 0) {
        suffix = "";
    } else if (threes == 1) {
        suffix = "K";
    } else if (threes == 2) {
        suffix = "M";
    } else if (threes == 3) {
        suffix = "T"
    } else {
        return n;
    }
    return Math.round(n/(Math.pow(10,3*threes))) + suffix;
}

$('.spotify.followers').each(function () {
    console.log($(this));
    let followers = parseInt($(this).attr("data-followers"));
    $(this).append(shortenNumber(followers) + " followers");
});
